import pytest
import re
from time import time
from conftest import InvalidCredentials



def test_create_user(api, as_admin):
    # create new invitation (send registration e-mail)
    email = '%s@example.com' % time()

    api.post('invitations/', json={
        'email': email,
    })

    # get token from mail
    last_message = as_admin.get('debug/mails')[-1]
    assert last_message['to'] == [email]
    activation_token = re.match(r'.*activate=(.*)', last_message['message'])\
        .groups()[0]

    # finish registration by clicking on the link in e-mail
    api.post(
        'users/',
        valid_status_codes=(204,),
        json={
            'token': activation_token,
            'password': 'my-password',
        })

    # log-in using the registered user
    me = api \
        .authenticate(email, 'my-password') \
        .get('users/me')

    # cleanup
    as_admin.delete(f'users/{me["id"]}')


def register_with_existing_email(api):
    response = api.post(
        'invitations/',
        valid_status_codes=(400,),
        json={'email': 'admin@example.com'},
    )
    assert 'email' in response  # error about e-mail


def register_with_invalid_email(api):
    # create the user
    response = api.post(
        'invitations/',
        valid_status_codes=(400,),
        json={'email': 'not-an-email'})
    # response adds information about the invalid field and the reason
    assert 'email' in response

def test_change_password(as_admin, api):
    email = 'test_password_change%s@example.com' %  time()

    # create new user
    user = as_admin.post('users/', {
        'username': email,
        'password': 'old_pass',
    })

    # change password
    api.authenticate(email, 'old_pass') \
        .patch('users/me/', {
        'old_password': 'old_pass',
        'password': 'new_pass',
    })

    # try authenticate using old password
    with pytest.raises(InvalidCredentials):
        api.authenticate(email, 'old_pass').get('users/me/')

    # authenticate using the new password
    api.authenticate(email, 'new_pass').get('users/me/')

    # cleanup
    as_admin.delete(f'users/{user["id"]}/')

