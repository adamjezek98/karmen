import unittest
import mock

from server.tasks.check_printers import check_printers


class Response:
    def __init__(self, status_code, contents={}):
        self.status_code = status_code
        self.contents = contents

    def json(self):
        return self.contents


class CheckPrintersTest(unittest.TestCase):
    @mock.patch(
        "server.database.printers.get_printers",
        return_value=[
            {
                "hostname": "a",
                "host": "1234",
                "client_props": {"connected": True, "version": {}, "read_only": False},
                "client": "octoprint",
                "protocol": "https",
                "printer_props": {"filament_type": "PETG"},
            },
            {
                "hostname": "b",
                "host": "5678",
                "client_props": {"connected": True, "version": {}, "read_only": False},
                "client": "octoprint",
            },
        ],
    )
    @mock.patch("server.database.printers.update_printer")
    @mock.patch("server.tasks.check_printers.redis")
    @mock.patch("server.clients.octoprint.requests.Session.get", return_value=None)
    def test_deactivate_no_data_responding_printer(
        self, mock_get_data, mock_redis, mock_update_printer, mock_get_printers
    ):
        check_printers()
        self.assertEqual(mock_get_printers.call_count, 1)
        self.assertEqual(mock_get_data.call_count, 2)
        self.assertEqual(mock_update_printer.call_count, 2)
        mock_update_printer.assert_has_calls(
            [
                mock.call(
                    **{
                        "hostname": "a",
                        "host": "1234",
                        "name": None,
                        "client": "octoprint",
                        "protocol": "https",
                        "client_props": {
                            "connected": False,
                            "version": {},
                            "read_only": False,
                            "protected": False,
                        },
                        "printer_props": {"filament_type": "PETG"},
                    }
                ),
                mock.call(
                    **{
                        "hostname": "b",
                        "host": "5678",
                        "protocol": "http",
                        "name": None,
                        "client": "octoprint",
                        "client_props": {
                            "connected": False,
                            "version": {},
                            "read_only": False,
                            "protected": False,
                        },
                        "printer_props": None,
                    }
                ),
            ]
        )

    @mock.patch(
        "server.database.printers.get_printers",
        return_value=[
            {
                "hostname": "a",
                "host": "1234",
                "client_props": {"connected": False, "version": {}, "read_only": False},
                "client": "octoprint",
                "protocol": "https",
            },
            {
                "hostname": "b",
                "host": "5678",
                "client_props": {"connected": True, "version": {}, "read_only": False},
                "client": "octoprint",
            },
        ],
    )
    @mock.patch("server.database.printers.update_printer")
    @mock.patch("server.clients.octoprint.requests.Session.get")
    @mock.patch("server.tasks.check_printers.redis")
    def test_activate_responding_printer(
        self, mock_redis, mock_get_data, mock_update_printer, mock_get_printers
    ):
        def mock_call(uri, **kwargs):
            if "5678" in uri and "/api/settings" in uri:
                return Response(
                    200,
                    {
                        "webcam": {
                            "webcamEnabled": True,
                            "streamUrl": "/webcam/?action=stream",
                            "flipH": False,
                            "flipV": True,
                            "rotate90": False,
                        }
                    },
                )
            return Response(200)

        mock_get_data.side_effect = mock_call
        check_printers()
        self.assertEqual(mock_get_printers.call_count, 1)
        self.assertEqual(
            mock_get_data.call_count, 5
        )  # Does an additional sniff request + 2 webcam requests
        self.assertEqual(mock_update_printer.call_count, 2)
        mock_update_printer.assert_has_calls(
            [
                mock.call(
                    **{
                        "hostname": "a",
                        "host": "1234",
                        "name": None,
                        "client": "octoprint",
                        "protocol": "https",
                        "client_props": {
                            "connected": True,
                            "version": {},
                            "read_only": False,
                            "protected": False,
                        },
                        "printer_props": None,
                    }
                ),
                mock.call(
                    **{
                        "hostname": "b",
                        "host": "5678",
                        "protocol": "http",
                        "name": None,
                        "client": "octoprint",
                        "client_props": {
                            "connected": True,
                            "version": {},
                            "read_only": False,
                            "protected": False,
                        },
                        "printer_props": None,
                    }
                ),
            ]
        )
        # 2 webcam requests for redis
        self.assertEqual(mock_redis.set.call_count, 1)
        self.assertEqual(mock_redis.delete.call_count, 1)
        mock_redis.set.assert_has_calls(
            [mock.call("webcam_5678", "http://5678/webcam/?action=stream")]
        )
        mock_redis.delete.assert_has_calls([mock.call("webcam_1234")])

    @mock.patch(
        "server.database.printers.get_printers",
        return_value=[
            {
                "hostname": "a",
                "host": "1234",
                "protocol": "https",
                "client_props": {"connected": False, "version": {}, "read_only": False},
                "client": "octoprint",
            },
            {
                "hostname": "b",
                "host": "5678",
                "client_props": {"connected": True, "version": {}, "read_only": False},
                "client": "octoprint",
            },
        ],
    )
    @mock.patch("server.database.printers.update_printer")
    @mock.patch("server.clients.octoprint.requests.Session.get")
    @mock.patch("server.tasks.check_printers.redis")
    @mock.patch("server.tasks.check_printers.app.logger")
    def test_no_fail_on_broken_redis(
        self,
        mock_logger,
        mock_redis,
        mock_get_data,
        mock_update_printer,
        mock_get_printers,
    ):
        def mock_call(uri, **kwargs):
            if "5678" in uri and "/api/settings" in uri:
                return Response(
                    200,
                    {
                        "webcam": {
                            "webcamEnabled": True,
                            "streamUrl": "/webcam/?action=stream",
                            "flipH": False,
                            "flipV": True,
                            "rotate90": False,
                        }
                    },
                )
            return Response(200)

        mock_get_data.side_effect = mock_call
        mock_redis.delete.side_effect = Exception("Cannot delete in redis")
        mock_redis.set.side_effect = Exception("Cannot set in redis")
        check_printers()
        self.assertEqual(mock_get_printers.call_count, 1)
        self.assertEqual(
            mock_get_data.call_count, 5
        )  # Does an additional sniff request + 2 webcam requests
        self.assertEqual(mock_update_printer.call_count, 2)
        mock_update_printer.assert_has_calls(
            [
                mock.call(
                    **{
                        "hostname": "a",
                        "host": "1234",
                        "name": None,
                        "protocol": "https",
                        "client": "octoprint",
                        "client_props": {
                            "connected": True,
                            "version": {},
                            "read_only": False,
                            "protected": False,
                        },
                        "printer_props": None,
                    }
                ),
                mock.call(
                    **{
                        "hostname": "b",
                        "host": "5678",
                        "name": None,
                        "protocol": "http",
                        "client": "octoprint",
                        "client_props": {
                            "connected": True,
                            "version": {},
                            "read_only": False,
                            "protected": False,
                        },
                        "printer_props": None,
                    }
                ),
            ]
        )
        # 2 webcam requests for redis
        self.assertEqual(mock_redis.set.call_count, 1)
        self.assertEqual(mock_redis.delete.call_count, 1)
        mock_redis.set.assert_has_calls(
            [mock.call("webcam_5678", "http://5678/webcam/?action=stream")]
        )
        mock_redis.delete.assert_has_calls([mock.call("webcam_1234")])
        self.assertEqual(mock_logger.error.call_count, 2)
