from base64 import urlsafe_b64encode
from time import time
from typing import Any

import respx
from authlib.jose import JsonWebKey, jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)
from httpx import Response


class StubAuthorizationServer:
    def __init__(self, resource_server_identifier: str) -> None:
        self._url = "https://stub.example"
        self._key_id = "stub_key"
        self._private_key, self._public_key = self._generate_key_pair()
        self._resource_server_identifier = resource_server_identifier

    @property
    def configuration_endpoint(self) -> str:
        return f"{self._url}/.well-known/openid-configuration"

    def create_access_token(
        self,
        issuer: str | None = None,
        audience: str | None = None,
        expiration_time: int | None = None,
        signature: bytes | None = None,
    ) -> str:
        subject = "stub_client_id"
        now = time()

        header = {
            "kid": self._key_id,
            "alg": "RS256",
        }

        payload = {
            "iss": issuer or self._url,
            "sub": subject,
            "aud": audience or self._resource_server_identifier,
            "exp": expiration_time or int(now + 60),
        }

        access_token: str = jwt.encode(header, payload, self._private_key).decode()

        if signature:
            access_token = self._replace_signature(access_token, signature)

        return access_token

    def given_configuration_endpoint_returns_configuration(self) -> None:
        respx.get(self.configuration_endpoint).mock(
            return_value=Response(200, json={"issuer": self._url, "jwks_uri": self._key_set_endpoint})
        )
        respx.get(self._key_set_endpoint).mock(return_value=Response(200, json=self._key_set()))

    @staticmethod
    def _generate_key_pair() -> tuple[bytes, bytes]:
        key_pair = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)
        private_key = key_pair.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        public_key = key_pair.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH)
        return private_key, public_key

    @property
    def _key_set_endpoint(self) -> str:
        return f"{self._url}/.well-known/jwks.json"

    def _key_set(self) -> dict[str, Any]:
        key = JsonWebKey.import_key(self._public_key, {"kty": "RSA", "kid": self._key_id})
        return {"keys": [key.as_dict()]}

    @staticmethod
    def _replace_signature(token: str, signature: bytes) -> str:
        header, body, _ = token.split(".")
        return ".".join([header, body, urlsafe_b64encode(signature).decode()])
