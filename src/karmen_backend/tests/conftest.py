from json.decoder import JSONDecodeError
from urllib.parse import urljoin
import pytest
import requests



API_URL = 'http://localhost:8000/api/2/'

# #########
# fixtures
# #########


@pytest.fixture
def as_admin():
    'ApiClient instance authorized with superuser'
    return ApiClient(API_URL).authenticate('admin', 'admin')


@pytest.fixture
def api():
    'A fresh ApiClient instance'
    return ApiClient(API_URL)


# ####################
# Supporting classes
######################

class ApiClient(object):
    '''
    Api client which logs in before doing any requests
    '''

    def __init__(self, base_url=API_URL):
        self._base_url = base_url
        self.tokens = None

    def _do_request(self, method, url, valid_status_codes=(200, 201, 204), **kwargs):
        if isinstance(valid_status_codes, int):
            valid_status_codes = (valid_status_codes,)
        session = requests.Session()

        url = urljoin(self._base_url, url)
        if self.tokens:
            session.headers.update({
                'authorization': f'Bearer {self.tokens["access"]}',
            })
        try:
            response = getattr(session, method)(url, **kwargs)
            if response.status_code == 403 and response.json().get('code') == 'token_not_valid':
                raise InvalidToken('Token is invalid: {response.json()["details"]}.')
            elif valid_status_codes is not None and response.status_code not in valid_status_codes:
                raise RuntimeError(f'Error response {response.status_code} {response.text[:300]}.')
            else:
                return JSONResponse(response)
        except JSONDecodeError:
            raise ValueError(f'Response {response.text[:300]} is not a json object.')

    def __call__(self, method, url, **kwargs):
        return self \
            ._do_request(method, url, **kwargs)

    def __getattr__(self, attr):
        '''
        Aliases http methods, e.g. self.get(**kwargs) to self('get', **kwargs)
        '''
        method = attr.lower()
        if method in ('get', 'post', 'delete', 'put', 'patch'):
            def wrapper(url, json=None, **kwargs):
                return self(method, url, json=json, **kwargs)
            return wrapper
        else:
            raise ValueError(f'Property {attr} does not exist.')

    def authenticate(self, username, password, lifetime=None):
        payload={
            'username': username,
            'password': password,
            }
        if lifetime is not None:
            payload['lifetime'] = lifetime
        response = self._do_request('post', 'tokens/', json=payload, valid_status_codes=(200,403,))
        if response.status_code == 403:
            raise InvalidCredentials(response)
        self.tokens = response.json()
        return self

    def logout(self):
        self.tokens = None
        return self

    def authenticate_refresh(self):
        if self.tokens is None or 'refresh' not in self.tokens:
            raise ValueError('No refresh token, authorize first.')
        else:
            self.tokens = self._do_request('post', 'tokens/refresh/', json={
                'refresh': self.tokens['refresh'],
            }).json()
        return self


class JSONResponse(object):
    '''
    Acts as dictionary / list containing json response while keeping Response
    properties like stats_code.
    '''
    def __init__(self, response):
        self._response = response
        self.__json = None

    def __getattr__(self, attr):
        return getattr(self._response, attr)

    def __getitem__(self, item):
        return self._json[item]

    def __len__(self):
        return len(self._json)

    def haskey(self, item):
        return item in self._json

    def __contains__(self, item):
        return self.haskey(item)

    @property
    def _json(self):
        if self.__json is None:
            try:
                self.__json = self._response.json()
            except JSONDecodeError:
                print(f'Response wast {self._response.status_code} "{self._response.text[:120]}"')
                raise
        return self.__json

class InvalidToken(RuntimeError):
    'token expired or is invalid'

class InvalidCredentials(RuntimeError):
    'authentication request denied with 403'
