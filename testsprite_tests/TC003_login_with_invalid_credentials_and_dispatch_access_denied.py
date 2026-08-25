import requests

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/accounts/login/"
DISPATCH_URL = f"{BASE_URL}/accounts/dispatch/"

def test_login_with_invalid_credentials_and_dispatch_access_denied():
    invalid_credentials = {
        "username": "invalid_user",
        "password": "wrong_password"
    }
    headers = {
        "Content-Type": "application/json"
    }

    # Attempt login with invalid credentials
    try:
        login_response = requests.post(
            LOGIN_URL,
            json=invalid_credentials,
            headers=headers,
            timeout=30,
            allow_redirects=False
        )
    except requests.RequestException as e:
        assert False, f"Login request failed: {e}"

    # Assert login response status code 400 or 401 or 403
    assert login_response.status_code in (400, 401, 403), \
        f"Expected login status 400, 401 or 403, got {login_response.status_code}"

    # Attempt dispatch without a valid session (no cookies)
    try:
        dispatch_response = requests.post(
            DISPATCH_URL,
            headers=headers,
            timeout=30,
            allow_redirects=False
        )
    except requests.RequestException as e:
        assert False, f"Dispatch request failed: {e}"

    # Assert dispatch response status code indicates access denied: 302 or 401 or 403
    assert dispatch_response.status_code in (302, 401, 403), \
        f"Expected dispatch status 302, 401 or 403, got {dispatch_response.status_code}"

test_login_with_invalid_credentials_and_dispatch_access_denied()