#!/usr/bin/env python3
from time import sleep
import pytest
from conftest import InvalidToken




def test_invalidate_token(as_admin):
    '''deletes active token (equivalent to logout) and tries to use it'''
    as_admin.delete('tokens/mine/', valid_status_codes=(204,))
    with pytest.raises(InvalidToken):
        as_admin.get('users/me/', valid_status_codes=(403,))


def test_expired_token(api):
    '''creates short-lived token and thies to use it after it's expiration time'''
    tokens = api.authenticate('admin', 'admin', 1)
    api.get('users/me', valid_status_codes=(200,))
    sleep(1.5)
    with pytest.raises(InvalidToken):
        api.get('users/me')

