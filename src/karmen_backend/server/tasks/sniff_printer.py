import uuid as guid

from server import app, celery
from server.database import printers
from server import clients


def save_printer_data(**kwargs):
    if not kwargs["client_props"]["connected"]:
        app.logger.info(
            "Printer on %s is not responding as connected" % kwargs.get("ip")
        )
        return
    has_record = printers.get_printer_by_network_props(
        kwargs.get("organization_uuid"),
        kwargs.get("hostname"),
        kwargs.get("ip"),
        kwargs.get("port"),
        kwargs.get("path"),
    )
    # No need to update registered printers
    if has_record is not None:
        app.logger.info(
            "Printer on %s is already registered within karmen" % kwargs.get("ip")
        )
        return
    printers.add_printer(
        **{
            "name": None,
            "client_props": {
                "connected": False,
                "version": {},
                "access_level": clients.utils.PrinterClientAccessLevel.PROTECTED,
            },
            **kwargs,
        }
    )


@celery.task(name="sniff_printer")
def sniff_printer(org_uuid, hostname, ip):
    app.logger.info("Sniffing printer on %s (%s) - trying http" % (ip, hostname))
    printer = clients.get_printer_instance(
        {
            "uuid": guid.uuid4(),
            "organization_uuid": org_uuid,
            "hostname": hostname,
            "ip": ip,
            "client": "octoprint",  # TODO not only octoprint
            "protocol": "http",
        }
    )

    printer.sniff()
    # Let's try a secured connection
    if not printer.client_info.connected:
        printer.protocol = "https"
        printer.update_network_base()
        app.logger.info("Sniffing printer on %s (%s) - trying https" % (ip, hostname))
        printer.sniff()

    # Not even on https, no reason to do anything
    if not printer.client_info.connected:
        app.logger.info("Sniffing printer on %s (%s) - no luck" % (ip, hostname))
        return

    app.logger.info("Sniffing printer on %s (%s) - success" % (ip, hostname))
    save_printer_data(
        uuid=printer.uuid,
        organization_uuid=org_uuid,
        name=hostname or ip,
        hostname=hostname,
        ip=ip,
        protocol=printer.protocol,
        client=printer.client_name(),
        client_props={
            "version": printer.client_info.version,
            "connected": printer.client_info.connected,
            "access_level": printer.client_info.access_level,
            "api_key": printer.client_info.api_key,
            "webcam": printer.webcam(),
            "plugins": printer.client_info.plugins,
        },
        printer_props=printer.get_printer_props(),
    )
