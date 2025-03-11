from authlib.jose import KeySet
from authlib.oauth2.rfc9068 import JWTBearerTokenGenerator


class StubJWTBearerTokenGenerator(JWTBearerTokenGenerator):  # type: ignore
    def __init__(self, issuer: str, jwks: KeySet):
        super().__init__(issuer)
        self._jwks = jwks

    def get_jwks(self) -> KeySet:
        return self._jwks
