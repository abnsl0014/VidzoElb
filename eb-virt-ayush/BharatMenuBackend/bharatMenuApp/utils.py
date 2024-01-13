import json
from urllib.request import urlopen
import requests

from authlib.oauth2.rfc7523 import JWTBearerTokenValidator
from authlib.jose.rfc7517.jwk import JsonWebKey


class Auth0JWTBearerTokenValidator(JWTBearerTokenValidator):
    def __init__(self, domain, audience):
        issuer = f"https://{domain}/"

        # print(f"{issuer}.well-known/jwks.json")

        response = requests.get(f"{issuer}.well-known/jwks.json")

        # print(response.text)

        # jsonurl = urlopen(f"{issuer}.well-known/jwks.json")

        # print(jsonurl.read())

        # print(jsonurl)

        # print(json.loads(jsonurl.read()))
        public_key = JsonWebKey.import_key_set(
            json.loads(response.text)
        )
        super(Auth0JWTBearerTokenValidator, self).__init__(
            public_key
        )
        self.claims_options = {
            "exp": {"essential": True},
            "aud": {"essential": True, "value": audience},
            "iss": {"essential": True, "value": issuer},
        }














# from django.contrib.auth import authenticate
# import json
# import jwt
# import requests

# def jwt_get_username_from_payload_handler(payload):
#     username = payload.get('sub').replace('|', '.')
#     authenticate(remote_user=username)
#     return username

# AUTH0_DOMAIN = "127.0.0.1:8000"
# AUTH0_AUDIENCE = "https://dev-2hnipz5fgv5putia.us.auth0.com/api/v2/"

# def jwt_decode_token(token):
#     header = jwt.get_unverified_header(token)
#     jwks = requests.get('http://{}/.well-known/jwks.json'.format('{AUTH0_DOMAIN}')).json()
#     public_key = None
#     for jwk in jwks['keys']:
#         if jwk['kid'] == header['kid']:
#             public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

#     if public_key is None:
#         raise Exception('Public key not found.')

#     issuer = 'http://{}/'.format('{AUTH0_DOMAIN}')
#     return jwt.decode(token, public_key, audience='{AUTH0_AUDIENCE}', issuer=issuer, algorithms=['RS256'])