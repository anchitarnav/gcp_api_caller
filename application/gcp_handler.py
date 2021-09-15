from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from enum import Enum, auto
from library import ApplicationException

import json


class GoogleRequests(Enum):
    GET = 'get'
    POST = 'post'


class AuthorisationType(Enum):
    SERVICE_ACCOUNT = auto()
    USER_AUTH = auto()


def check_valid_creds(json_string):
    if not json_string:
        return False, "No cred info present"
    try:
        json.loads(json_string)
    except json.JSONDecodeError:
        return False, "Illegal/ Malformed JSON"
    else:
        return True, "Credential validation Successful"


def get_authorised_session(authorisation_type, key_contents=None):
    if authorisation_type is AuthorisationType.SERVICE_ACCOUNT and not key_contents:
        raise ApplicationException('Key Contents empty or not passed')

    try:
        service_account_info = json.loads(key_contents)
    except json.JSONDecodeError:
        raise ApplicationException('Illegal JSON object passed for key')

    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    scoped_credentials = credentials.with_scopes(
        ['https://www.googleapis.com/auth/cloud-platform'])
    return AuthorizedSession(scoped_credentials)


def make_request(request_type: str, auth_session: AuthorizedSession, request_url: str, data: dict = None):
    """
    :param request_url:
    :param request_type:
    :param auth_session:
    :param data:
    :return:
    """
    request_params = {
        'method': request_type,
        'url': request_url,
    }

    if data:
        request_params['data'] = data

    res = auth_session.request(**request_params)
    return res.status_code, res.text
