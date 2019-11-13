import base64
import json
import unittest

from server import app


def get_token_data(jwtoken):
    information = jwtoken.split(".")[1]
    information += "=" * (-len(information) % 4)
    return json.loads(base64.b64decode(information, "-_"))


class AuthenticateRoute(unittest.TestCase):
    def test_no_data(self):
        with app.test_client() as c:
            response = c.post("/users/authenticate")
            self.assertEqual(response.status_code, 400)

    def test_missing_username(self):
        with app.test_client() as c:
            response = c.post("/users/authenticate", json={"password": "random"})
            self.assertEqual(response.status_code, 400)

    def test_missing_password(self):
        with app.test_client() as c:
            response = c.post("/users/authenticate", json={"username": "random"})
            self.assertEqual(response.status_code, 400)

    def test_unknown_user(self):
        with app.test_client() as c:
            response = c.post(
                "/users/authenticate", json={"username": "random", "password": "random"}
            )
            self.assertEqual(response.status_code, 401)

    def test_bad_password(self):
        with app.test_client() as c:
            response = c.post(
                "/users/authenticate",
                json={"username": "test-admin", "password": "random"},
            )
            self.assertEqual(response.status_code, 401)

    def test_returns_fresh_access_token(self):
        with app.test_client() as c:
            response = c.post(
                "/users/authenticate",
                json={"username": "test-admin", "password": "admin-password"},
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue("access_token" in response.json)
            self.assertTrue("refresh_token" in response.json)
            data = get_token_data(response.json["access_token"])
            self.assertEqual(data["fresh"], True)
            self.assertEqual(data["type"], "access")
            self.assertEqual(data["identity"], "6480fa7d-ce18-4ae2-818b-f1d200050806")
            self.assertTrue("user_claims" in data)
            self.assertTrue("role" in data["user_claims"])
            self.assertTrue("force_pwd_change" in data["user_claims"])


class AuthenticateFreshRoute(unittest.TestCase):
    def test_no_data(self):
        with app.test_client() as c:
            response = c.post("/users/authenticate-fresh")
            self.assertEqual(response.status_code, 400)

    def test_missing_username(self):
        with app.test_client() as c:
            response = c.post("/users/authenticate-fresh", json={"password": "random"})
            self.assertEqual(response.status_code, 400)

    def test_missing_password(self):
        with app.test_client() as c:
            response = c.post("/users/authenticate-fresh", json={"username": "random"})
            self.assertEqual(response.status_code, 400)

    def test_unknown_user(self):
        with app.test_client() as c:
            response = c.post(
                "/users/authenticate-fresh",
                json={"username": "random", "password": "random"},
            )
            self.assertEqual(response.status_code, 401)

    def test_bad_password(self):
        with app.test_client() as c:
            response = c.post(
                "/users/authenticate-fresh",
                json={"username": "test-admin", "password": "random"},
            )
            self.assertEqual(response.status_code, 401)

    def test_returns_fresh_access_token(self):
        with app.test_client() as c:
            response = c.post(
                "/users/authenticate-fresh",
                json={"username": "test-admin", "password": "admin-password"},
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue("access_token" in response.json)
            self.assertTrue("refresh_token" not in response.json)
            data = get_token_data(response.json["access_token"])
            self.assertEqual(data["fresh"], True)
            self.assertEqual(data["type"], "access")
            self.assertEqual(data["identity"], "6480fa7d-ce18-4ae2-818b-f1d200050806")
            self.assertTrue("user_claims" in data)
            self.assertTrue("role" in data["user_claims"])
            self.assertTrue("force_pwd_change" in data["user_claims"])


class AuthenticateRefreshRoute(unittest.TestCase):
    def setUp(self):
        with app.test_client() as c:
            response = c.post(
                "/users/authenticate",
                json={"username": "test-admin", "password": "admin-password"},
            )
            self.jwt = response.json["refresh_token"]

    def test_no_token(self):
        with app.test_client() as c:
            response = c.post("/users/authenticate-refresh")
            self.assertEqual(response.status_code, 401)

    def test_bad_token(self):
        with app.test_client() as c:
            response = c.post(
                "/users/authenticate-refresh",
                headers={
                    "Authorization": "Bearer %s"
                    % (
                        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ0b3B0YWwuY29tIiwiZXhwIjoxNDI2NDIwODAwLCJodHRwOi8vdG9wdGFsLmNvbS9qd3RfY2xhaW1zL2lzX2FkbWluIjp0cnVlLCJjb21wYW55IjoiVG9wdGFsIiwiYXdlc29tZSI6dHJ1ZX0.yRQYnWzskCZUxPwaQupWkiUzKELZ49eM7oWxAQK_ZXw",
                    )
                },
            )
            self.assertEqual(response.status_code, 422)

    def test_returns_nonfresh_access_token(self):
        with app.test_client() as c:
            response = c.post(
                "/users/authenticate-refresh",
                headers={"Authorization": "Bearer %s" % (self.jwt,)},
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue("access_token" in response.json)
            self.assertTrue("refresh_token" not in response.json)
            data = get_token_data(response.json["access_token"])
            self.assertEqual(data["fresh"], False)
            self.assertEqual(data["type"], "access")
            self.assertEqual(data["identity"], "6480fa7d-ce18-4ae2-818b-f1d200050806")
            self.assertTrue("user_claims" in data)
            self.assertTrue("role" in data["user_claims"])
            self.assertTrue("force_pwd_change" in data["user_claims"])


class ChangePasswordRoute(unittest.TestCase):
    def setUp(self):
        with app.test_client() as c:
            response = c.post(
                "/users/authenticate",
                json={"username": "test-admin", "password": "admin-password"},
            )
            self.jwt = response.json["access_token"]
            response = c.post(
                "/users/authenticate-refresh",
                headers={
                    "Authorization": "Bearer %s" % (response.json["refresh_token"],)
                },
            )
            self.nonfresh_jwt = response.json["access_token"]

    def test_missing_jwt(self):
        with app.test_client() as c:
            response = c.patch(
                "/users/6480fa7d-ce18-4ae2-818b-f1d200050806",
                json={
                    "password": "random",
                    "new_password_confirmation": "random",
                    "new_password": "random",
                },
            )
            self.assertEqual(response.status_code, 401)

    def test_nonfresh_jwt(self):
        with app.test_client() as c:
            response = c.patch(
                "/users/6480fa7d-ce18-4ae2-818b-f1d200050806",
                headers={"Authorization": "Bearer %s" % (self.nonfresh_jwt,)},
                json={
                    "password": "random",
                    "new_password_confirmation": "random",
                    "new_password": "random",
                },
            )
            self.assertEqual(response.status_code, 401)
            self.assertTrue("Fresh token required" in response.json["message"])

    def test_mismatch_token_uuid(self):
        with app.test_client() as c:
            response = c.patch(
                "/users/77315957-8ebb-4a44-976c-758dbf28bb9f",
                headers={"Authorization": "Bearer %s" % (self.jwt,)},
                json={
                    "password": "user-password",
                    "new_password_confirmation": "random",
                    "new_password": "random",
                },
            )
            self.assertEqual(response.status_code, 401)

    def test_no_data(self):
        with app.test_client() as c:
            response = c.patch(
                "/users/6480fa7d-ce18-4ae2-818b-f1d200050806",
                headers={"Authorization": "Bearer %s" % (self.jwt,)},
            )
            self.assertEqual(response.status_code, 400)

    def test_missing_new_password(self):
        with app.test_client() as c:
            response = c.patch(
                "/users/6480fa7d-ce18-4ae2-818b-f1d200050806",
                headers={"Authorization": "Bearer %s" % (self.jwt,)},
                json={"password": "random", "new_password_confirmation": "random"},
            )
            self.assertEqual(response.status_code, 400)

    def test_missing_new_password_confirmation(self):
        with app.test_client() as c:
            response = c.patch(
                "/users/6480fa7d-ce18-4ae2-818b-f1d200050806",
                headers={"Authorization": "Bearer %s" % (self.jwt,)},
                json={"password": "random", "new_password": "random"},
            )
            self.assertEqual(response.status_code, 400)

    def test_missing_password(self):
        with app.test_client() as c:
            response = c.patch(
                "/users/6480fa7d-ce18-4ae2-818b-f1d200050806",
                headers={"Authorization": "Bearer %s" % (self.jwt,)},
                json={"new_password_confirmation": "random", "new_password": "random"},
            )
            self.assertEqual(response.status_code, 400)

    def test_unknown_user(self):
        with app.test_client() as c:
            response = c.patch(
                "/users/6480fa7d-ce18-4ae2-1234-f1d200050806",
                headers={"Authorization": "Bearer %s" % (self.jwt,)},
                json={
                    "new_password_confirmation": "random",
                    "new_password": "random",
                    "password": "admin-password",
                },
            )
            self.assertEqual(response.status_code, 401)

    def test_bad_password(self):
        with app.test_client() as c:
            response = c.patch(
                "/users/6480fa7d-ce18-4ae2-818b-f1d200050806",
                json={
                    "new_password_confirmation": "random",
                    "new_password": "random",
                    "password": "bad-password",
                },
            )
            self.assertEqual(response.status_code, 401)

    def test_new_pwd_mismatch(self):
        with app.test_client() as c:
            response = c.patch(
                "/users/6480fa7d-ce18-4ae2-818b-f1d200050806",
                headers={"Authorization": "Bearer %s" % (self.jwt,)},
                json={
                    "new_password_confirmation": "random",
                    "new_password": "random-mismatch",
                    "password": "admin-password",
                },
            )
            self.assertEqual(response.status_code, 400)

    def test_bad_pwd(self):
        with app.test_client() as c:
            response = c.patch(
                "/users/6480fa7d-ce18-4ae2-818b-f1d200050806",
                headers={"Authorization": "Bearer %s" % (self.jwt,)},
                json={
                    "new_password_confirmation": "random",
                    "new_password": "random",
                    "password": "bad-password",
                },
            )
            self.assertEqual(response.status_code, 401)

    def test_pwd_changed(self):
        with app.test_client() as c:
            change = c.patch(
                "/users/6480fa7d-ce18-4ae2-818b-f1d200050806",
                headers={"Authorization": "Bearer %s" % (self.jwt,)},
                json={
                    "new_password_confirmation": "random",
                    "new_password": "random",
                    "password": "admin-password",
                },
            )
            self.assertEqual(change.status_code, 200)
            auth = c.post(
                "/users/authenticate",
                json={"username": "test-admin", "password": "random"},
            )
            self.assertEqual(auth.status_code, 200)
            change_back = c.patch(
                "/users/6480fa7d-ce18-4ae2-818b-f1d200050806",
                headers={"Authorization": "Bearer %s" % (auth.json["access_token"],)},
                json={
                    "new_password_confirmation": "admin-password",
                    "new_password": "admin-password",
                    "password": "random",
                },
            )
            self.assertEqual(change_back.status_code, 200)