from hashlib import md5
from django.core.cache import cache
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, Token
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.utils import datetime_from_epoch

BLACKLIST_KEY_PREFIX = 'token-blacklisted-'


class InvalidableTokenMixin(object):
    def verify(self):
        super().verify()
        if cache.get(self._cache_key):
            raise TokenError('Token is not valid.')

    def blacklist(self):
        cache.set(self._cache_key, 1, self.time_remining().seconds)

    def expires_at(self):
        claim_value = self.payload['exp']
        return datetime_from_epoch(claim_value)

    def time_remining(self):
        return self.current_time - self.expires_at()

    @property
    def _cache_key(self):
        token_hash = md5(str(self).encode()).hexdigest()
        return '%s-%s' % (BLACKLIST_KEY_PREFIX, token_hash)


class KarmenAccessToken(InvalidableTokenMixin, AccessToken):
    '''Instantionate during authentication - request.auth will contain this
    token.'''


class KarmenRefreshToken(InvalidableTokenMixin, RefreshToken):
    pass


class EmailVerificationToken(Token):
    '''
    A token dedicated for e-mail verification.
    '''
    token_type = 'email-validation'
    lifetime = settings.EMAIL_VALIDATION_LIFETIME

    @classmethod
    def for_email(cls, email):
        token = cls()
        token['sub'] = email
        return token

