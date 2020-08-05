# Karmen backend II.

## Installation

    git clone git@bitbucket.org:fragariacz/karmen-backend2.git
    cd karmen-backend2
    pipenv install -r requirements.pip -r requirements-dev.pip
    pipenv run karmen/manage.py migrate
    pipenv run karmen/manage.py runserver

Open `http://localhost:8000/api/2`. If you see:


```
GET /api/2/

HTTP 403 Forbidden
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "detail": "Authentication credentials were not provided."
}
```

then you just installed Karmen backend II.

If you want to insert some testing data to start playing call

```
    pipenv run karmen/manage.py generate_test_data
```

Now you should be able to login in `/api/2`
- as user: `user@example.com` / password `user` or
- as admin: `admin` with password `admin`.

Try to open /api/2/ again when you are logged in. You should see

```
GET /api/2/

HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "invitations": "http://localhost:8000/api/2/invitations/",
    "users/me/printers": "http://localhost:8000/api/2/users/me/printers/",
    "users": "http://localhost:8000/api/2/users/",
    "tokens": "http://localhost:8000/api/2/tokens/",
    "printers": "http://localhost:8000/api/2/printers/"
}
```

This is list of main API endpoints.

The main endpoints for your user data are under `/users/me/`:

- /api/2/users/me/
- /api/2/users/me/printers/
- /api/2/users/me/groups/

If you want to include an octoprint response set `api_key` in a printer object to
url to octoprint api. For example: `http://localhost:8080/api/?apikey=<api_key>`
This is development hack which is not meant to be kept in final application.

Look in [test_users](./tests/test_users.py) to see how to register as a new user.

For examples and informations on how to use the API look in [tests](./tests).

## Development

## Project layout

Karmen is a [Django Framework](https://docs.djangoproject.com/) project with
[Django Rest Framework](https://www.django-rest-framework.org/). For
information on filesystem structrure refere to django documentation or
[djangobook](https://djangobook.com/mdj2-django-structure/) 

**Main parts**

- debugging_tools - various tools used during debugging / testing. This app is
  installed only when `DEBUG` is set to `True`.
- [users](./karmen/users) - app - custom user model which extends Django's own User
- [printers](./karmen/printers) - app - configured printers
     - [octoprint.py](./karmen/printers/octoprint.py) - octoprint connector
- [groups](./karmen/groups) - app - puts printers and users together.
- [files](./karmen/files) - app - uploaded files (gcodes under former Karmen Backend)


### Conventions

- Object level access permission model is implemented in
  [ObjectLevelAccessRestrictionViewSetMixin](./karmen/karmen/viewsets.py). It expects that
  objects has methods `can_view(user)`, `can_modify(user)` and
  `can_delete(user)`. The latest defaults to `can_modify(user)` when omitted.
- Currently, User is expected to have e-mail in username. This is not good
  solution and is subject to change.

### API tests

There are growing API [tests](./tests) in root directory. These tests should
use API only and are completely independent on backend implementation -
therefor no mocks should be used.

#### api fixture

To make testing more comfortable, you can use `api` pytest fixture with [api
client](./tests/conftest.py). The usage is simple. For example to list user printers
`api.get('users/me/printers/')`, to add printer: `api.post(`printers`, {'name':
'My new printer'})`. There is also `as_admin` fixture which contains `api`
authenticated as admin user (expects user `admin` with password `admin`) in
test database.



### E-mails

When django's `locmem` e-mail backend is used (default for development) and
`DEBUG=True` under settings, sent e-mail messages are accessible on
`/api/2/debug/mails` (you have to be logged in as `admin`). This is
particularly useful for invitation debugging.

### Octoprint with virtual printer

- Checkout OctoPrint: `git clone https://github.com/OctoPrint/OctoPrint.git`
- Change into the OctoPrint folder: `cd OctoPrint`
- Create a user-owned virtual environment therein: `virtualenv venv`
- Install OctoPrint into that virtual environment: `./venv/bin/pip install .`
- run `octoprint server --host=127.0.0.1 --port=8080`

*Source https://github.com/OctoPrint/OctoPrint#usage*

**Add virtual printer**

Open octoprint configuration file
- Linux: `~/.octoprint/config.yaml`
- macOs: `~/Library/Application Support/OctoPrint/config.yaml`

Add following lines:

```
devel:
  virtualPrinter:
    enabled: true
```

Restart octoprint.
To connect to virtual printer select `VIRTUAL` under serial port.

*Source: https://docs.octoprint.org/en/master/development/virtual_printer.html*
