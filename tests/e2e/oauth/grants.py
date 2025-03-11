from authlib.oauth2.rfc6749 import ClientCredentialsGrant


class ClientSecretPostClientCredentialsGrant(ClientCredentialsGrant):  # type: ignore
    TOKEN_ENDPOINT_AUTH_METHODS = ["client_secret_post"]
