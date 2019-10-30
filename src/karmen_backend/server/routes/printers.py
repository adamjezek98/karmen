import re

import requests
from flask import jsonify, request, abort, Response, stream_with_context
from flask_cors import cross_origin
from server import app, __version__
from server.database import printers
from server import clients
from server.services import network


def make_printer_response(printer, fields):
    printer_inst = clients.get_printer_instance(printer)
    data = {
        "client": {
            "name": printer_inst.client_name(),
            "version": printer_inst.client.version,
            "connected": printer_inst.client.connected,
            "readonly": printer_inst.client.read_only,
            "protected": bool(printer_inst.client.protected),
        },
        "printer_props": printer_inst.get_printer_props(),
        "name": printer_inst.name,
        "hostname": printer_inst.hostname,
        "host": printer_inst.host,
        "protocol": printer_inst.protocol,
    }
    if "status" in fields:
        data["status"] = printer_inst.status()
    if "webcam" in fields:
        data["webcam"] = printer_inst.webcam()
        if "stream" in data["webcam"]:
            data["webcam"]["proxied"] = "/proxied-webcam/%s" % (printer_inst.host,)
    if "job" in fields:
        data["job"] = printer_inst.job()
    return data


@app.route("/printers", methods=["GET", "OPTIONS"])
@cross_origin()
def printers_list():
    device_list = []
    fields = [f for f in request.args.get("fields", "").split(",") if f]
    for printer in printers.get_printers():
        # TODO this should somehow go in parallel
        device_list.append(make_printer_response(printer, fields))
    return jsonify({"items": device_list})


@app.route("/printers", methods=["POST", "OPTIONS"])
@cross_origin()
def printer_create():
    data = request.json
    if not data:
        return abort(400)
    host = data.get("host", None)
    name = data.get("name", None)
    protocol = data.get("protocol", "http")
    if (
        not host
        or not name
        or protocol not in ["http", "https"]
        or re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:?\d{0,5}$", host) is None
    ):
        return abort(400)
    if printers.get_printer(host) is not None:
        return abort(409)
    hostname = network.get_avahi_hostname(host)
    printer = clients.get_printer_instance(
        {
            "hostname": hostname,
            "host": host,
            "name": name,
            "protocol": protocol,
            "client": "octoprint",  # TODO make this more generic
        }
    )
    printer.sniff()
    printers.add_printer(
        name=name,
        hostname=hostname,
        host=host,
        protocol=printer.protocol,
        client=printer.client_name(),
        client_props={
            "version": printer.client.version,
            "connected": printer.client.connected,
            "read_only": printer.client.read_only,
            "protected": printer.client.protected,
        },
    )
    return "", 201


@app.route("/printers/<host>", methods=["GET", "OPTIONS"])
@cross_origin()
def printer_detail(host):
    fields = request.args.get("fields").split(",") if request.args.get("fields") else []
    printer = printers.get_printer(host)
    if printer is None:
        return abort(404)
    return jsonify(make_printer_response(printer, fields))


@app.route("/printers/<host>", methods=["DELETE", "OPTIONS"])
@cross_origin()
def printer_delete(host):
    printer = printers.get_printer(host)
    if printer is None:
        return abort(404)
    printers.delete_printer(host)
    return "", 204


@app.route("/printers/<host>", methods=["PATCH", "OPTIONS"])
@cross_origin()
def printer_patch(host):
    printer = printers.get_printer(host)
    if printer is None:
        return abort(404)
    data = request.json
    if not data:
        return abort(400)
    name = data.get("name", None)
    protocol = data.get("protocol", printer["protocol"])
    if not name or protocol not in ["http", "https"]:
        return abort(400)
    printer_inst = clients.get_printer_instance(printer)
    printer_props = data.get("printer_props", {})
    if printer_props:
        if not printer_inst.get_printer_props():
            printer_inst.printer_props = {}
        printer_inst.get_printer_props().update(
            {
                k: printer_props[k]
                for k in [
                    "filament_type",
                    "filament_color",
                    "bed_type",
                    "tool0_diameter",
                ]
                if k in printer_props
            }
        )
    printers.update_printer(
        name=name,
        hostname=printer_inst.hostname,
        host=printer_inst.host,
        protocol=protocol,
        client=printer_inst.client_name(),
        client_props={
            "version": printer_inst.client.version,
            "connected": printer_inst.client.connected,
            "read_only": printer_inst.client.read_only,
            "protected": printer_inst.client.protected,
        },
        printer_props=printer_inst.get_printer_props(),
    )
    return "", 204


@app.route("/printers/<host>/connection", methods=["POST", "OPTIONS"])
@cross_origin()
def printer_change_connection(host):
    printer = printers.get_printer(host)
    if printer is None:
        return abort(404)
    data = request.json
    if not data:
        return abort(400)
    state = data.get("state", None)
    printer_inst = clients.get_printer_instance(printer)
    if state == "online":
        r = printer_inst.connect_printer()
        return (
            ("", 204)
            if r
            else ("Cannot change printer's connection state to online", 500)
        )
    elif state == "offline":
        r = printer_inst.disconnect_printer()
        return (
            ("", 204)
            if r
            else ("Cannot change printer's connection state to offline", 500)
        )
    else:
        return abort(400)
    return "", 204


@app.route("/printers/<host>/current-job", methods=["POST", "OPTIONS"])
@cross_origin()
def printer_modify_job(host):
    printer = printers.get_printer(host)
    if printer is None:
        return abort(404)
    data = request.json
    if not data:
        return abort(400)
    action = data.get("action", None)
    if not action:
        return abort(400)
    printer_inst = clients.get_printer_instance(printer)
    try:
        if printer_inst.modify_current_job(action):
            return "", 204
        return "", 409
    except clients.utils.PrinterClientException as e:
        return abort(400, e)


@app.route("/proxied-webcam/<host>", methods=["GET", "OPTIONS"])
@cross_origin()
def printer_webcam(host):
    # This is very inefficient and should not be used in production. Use the nginx
    # redis based proxy pass instead
    # TODO maybe we can drop this in the dev env as well
    printer = printers.get_printer(host)
    if printer is None:
        return abort(404)
    printer_inst = clients.get_printer_instance(printer)
    webcam = printer_inst.webcam()
    if "stream" not in webcam:
        return abort(404)
    req = requests.get(webcam["stream"], stream=True)
    return Response(
        stream_with_context(req.iter_content()),
        content_type=req.headers["content-type"],
    )
