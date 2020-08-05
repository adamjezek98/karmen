from urllib.parse import urljoin
from requests import request
from karmen.utils import lock_cached


class DeviceError(RuntimeError):
    '''general client error'''

class UnparsableResponseError(DeviceError):
    '''we were unable to parse the response'''

class PermissionDeniedError(DeviceError):
    '''The access to the device was forbiden'''

class ConflictError(DeviceError):
    '''The device indicates that there is a conflict'''

class PrinterNotOperationalError(DeviceError):
    '''The device indicates that the printer is not in operational state (not connected).'''


class OctoprintClient(object):
    '''
    Octoprint client class
    
    This class is responsible to communicate with octoprint devices

    @see [Readme](../../../README.md) for instructions on how to setup testing octoprint server for development.
    
    '''

    def __init__(self, api_uri, api_key=None):
        self._base_api_uri = '%s/' % api_uri.rstrip('/')
        '''uri to the base endpoint of octoprint API'''
        self.api_key = api_key
        '''api key needed to access Octoprint server'''
        self.status = None
        '''current printer status'''

    def _make_request(self, method, path, **kwargs):
        '''
        Performs request to configured device api using 

        :param str method: http method, GET, POST, ...
        :param str path: relative path to api_uri (set in __init__)
        :param **kwargs: other keyword arguments directly passed to requests.request method
        :return
        Returns
        -------
        mixed
            parsed response body (dict for json or None for `204 / 201 http
            response. Other response types could be added (e.g. file download).

        Central method for making http request to devices. Any client http
        request goes through this method.

        This method always returns parsed success response. Any error response
        is raised as an exception for further processiong by upper layers.
        Exceptions caused by the device (should inherit from DeviceError).
        '''
        path = path.lstrip('/')
        url = urljoin(self._base_api_uri, path)
        params = kwargs.pop('params', {})
        if self.api_key:
            params['apikey'] = self.api_key
        response = request(method, url, params=params, **kwargs)
        if response.status_code == 200:
            if response.json:
                data = response.json()
            else:
                raise UnparsableResponseError('The client response does not contain a json content.')
        elif response.status_code in (204, 201, ):
            data = None
        elif response.status_code == 403:
            raise PermissionDeniedError('The device indicates that we do not have access to the resource.')
        elif response.status_code == 409:
            raise ConflictError(response.content)
        else:
            raise DeviceError(f'Got an unexpected response {response.status_code} {response.reason} from the device.')
        return data

    def _get(self, path, **kwargs):
        '''
        Shortcut to GET HTTP method (protected)

        Kwargs are used as query params which is the most common case for GET
        method.
        '''
        return self._make_request('get', path, params=kwargs)

    def _post(self, path, **kwargs):
        '''Shortcut to POST HTTP method (protected)'''
        return self._make_request('post', path, **kwargs)

    @lock_cached(ttl=15)
    def get_version(self):
        return self._get('version')

    @lock_cached(ttl=5)
    def get_connection(self):
        return self._get('connection')

    @lock_cached(ttl=15)
    def list_files(self, location='local'):
        return self._get(urljoin('files/', location))

    def upload_file(self, filename, location='local', foldername=None, start_print=False):
        '''
        Upload file to location.
        Raises ConflictError if the file already exists.
        '''
        path = urljoin('files/', location)
        form_data = {}
        if foldername:
            form_data['foldername'] = {None: foldername}
        if print:
            form_data['print'] = str(start_print).lower()
        with open(filename, 'rb') as file:
            form_data['file'] = file
            response = self._post(path, files=form_data)
        self.list_files.invalidate_cache(location=location)
        return response

    def delete_file(self, filepath, location='local'):
        '''
        Deletes file on `filepath` from the device.
        Raises ConflictError if the file is being printed currently.
        '''
        response = delete(urljoin('files/', location, filepath))
        self.list_files.invalidate_cache(location=location)
        return response

    def print_file(self, filename):
        '''
        Prints previously uploaded file
        '''
        path = urljoin('files/', filepath)
        data={'command': 'select', 'print': True}
        return self._post(path, json=data)

    @lock_cached(ttl=5)
    def get_printer(self, history=False):
        history = str(history).lower()
        try:
            return self._get('printer', history=history)
        except ConflictError as e:
            raise PrinterNotOperationalError(e)
