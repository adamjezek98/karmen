import pickle
from hashlib import md5
from random import randint
from django.core.cache import cache
from django.conf import settings
from django_lock import lock
from base36 import dumps as b36encode


MAX_RAND = 36**settings.ID_FIELD_LENGTH


def gen_short_uid():
    '''
    Used to generate pk for models.

    This approach is nearly as safe as uuid and much easier to use.
    '''
    return b36encode(randint(0, MAX_RAND))[:settings.ID_FIELD_LENGTH]


def build_cache_key(prefix, method, args, kwargs):
    kwargs_key = ','.join(sorted(kwargs.items()))
    args_key = ','.join(args)
    key = '%s_%s: %s(%s, %s)' % (prefix, method.__module__, method.__qualname__, args_key, kwargs_key)
    return md5(key.encode('utf-8')).hexdigest()


def lock_cached(method=None, ttl=1, lock_timeout=None, key_prefix='restricted_cache-decorator'):
    '''
    Cache method with a global lock using django's cache framework

    Usage:

    class Somthing:

        @lock_cached(ttl=60)
        def list_files(self, disk):
            ...
            return file_list

        def delete_file(self, disk, filepath):
            ...
            self.list_files.invalidate_cache(disk)


    Note: Highly inspired by django's @cached_property.
    '''
    lock_timeout = ttl if lock_timeout is None else lock_timeout

    def invalidate(*args, **kwargs):
        key = build_cache_key(key_prefix, method, args, kwargs)
        cache.delete(*args, **kwargs)

    def decorator(method):
        def wrap(self, *args, **kwargs):
            key = build_cache_key(key_prefix, method, args, kwargs)
            with lock(key, timeout=lock_timeout):
                value = cache.get(key)
                if value is not None:
                    value = pickle.loads(value)
                else:
                    value = method(self, *args, **kwargs)
                    cache.set(key, pickle.dumps(value), timeout=ttl)
                return value
        wrap.invalidate_cache = invalidate
        return wrap

    if method:
        # This was an actual decorator call, ex: @cached_property
        wrapped = decorator(method)
    else:
        # This is a factory call, ex: @cached_property()
        wrapped = decorator

    return wrapped


class classproperty(object):
    '''same as @property decorator but for class - read-only'''

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)
