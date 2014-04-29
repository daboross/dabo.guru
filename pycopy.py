import json
from urllib.parse import urlencode

from requests_oauthlib import OAuth1Session


def request_token(app_key, app_secret, callback_url):
    """
    Completes most of the steps to get a new access token, given the application key and secret.

    This method returns the URL that the user should be sent to to confirm authorization.
    You can then use the redirect URL from that to get data. The redirect url will be in the format of:
    `<callback_url>?oauth_token=<token>&oauth_verifier=<verifier>

    After getting the token and verifier, use the get_access_token() method to get your access keys.
    :param app_key: The application key
    :param app_secret: The application secret
    :param callback_url: The url to pass as the callback url
    :return: The user key, and the user secret
    :type app_key: str
    :type app_secret: str
    :rtype: str
    """
    request_token_url = "https://api.copy.com/oauth/request?{}".format(urlencode(
        {"scope": json.dumps({"filesystem": {"read": True, "write": True}})}
    ))
    base_authorization_url = "https://www.copy.com/applications/authorize"

    copy_session = OAuth1Session(app_key, app_secret, callback_uri=callback_url)

    copy_session.fetch_request_token(request_token_url)

    authorization_url = copy_session.authorization_url(base_authorization_url)

    return authorization_url


def get_access_token(app_key, app_secret, oauth_token, oauth_verifier):
    """
    This is the final method for the authentication process

    It will take the application key, application secret, and the oauth_token and oauth_verifier gotten from the
    callback URL.


    :param app_key: Application key
    :param app_secret: Application secret
    :param oauth_token: OAuth token
    :param oauth_verifier: OAuth verifier token
    """
    print(app_key, app_secret, oauth_token, oauth_verifier)
    copy_session = OAuth1Session(app_key, app_secret, oauth_token, oauth_verifier)

    oauth_tokens = copy_session.fetch_access_token("https://api.copy.com/oauth/access")

    return oauth_tokens["oauth_token"], oauth_tokens["oauth_token_secret"]
