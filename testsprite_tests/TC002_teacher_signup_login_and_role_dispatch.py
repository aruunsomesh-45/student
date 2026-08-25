import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def get_csrf_token(session, url):
    resp = session.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    # Extract CSRF token from cookies
    return session.cookies.get('csrftoken', '')

def test_teacher_signup_login_and_role_dispatch():
    session = requests.Session()
    try:
        # Step 0: Get CSRF token from signup page
        signup_page_url = f"{BASE_URL}/accounts/signup/teacher/"
        csrf_token = get_csrf_token(session, signup_page_url)

        # Step 1: Teacher registration
        signup_url = f"{BASE_URL}/accounts/signup/teacher/"
        teacher_signup_payload = {
            "username": "testteacher001",
            "password1": "StrongPass!2026",
            "password2": "StrongPass!2026",
            "email": "testteacher001@example.com",
            "first_name": "Test",
            "last_name": "Teacher"
        }
        signup_headers = {
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token
        }
        signup_resp = session.post(signup_url, json=teacher_signup_payload, headers=signup_headers, timeout=TIMEOUT)
        assert signup_resp.status_code in (200, 201), f"Unexpected signup status: {signup_resp.status_code}, content: {signup_resp.text}"

        # Step 2: Login with registered teacher credentials
        # Get CSRF token again from login page
        login_page_url = f"{BASE_URL}/accounts/login/"
        csrf_token = get_csrf_token(session, login_page_url)

        login_url = f"{BASE_URL}/accounts/login/"
        login_payload = {
            "username": "testteacher001",
            "password": "StrongPass!2026"
        }
        # Use form-encoded data instead of JSON
        login_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrf_token
        }
        login_resp = session.post(login_url, data=login_payload, headers=login_headers, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}, content: {login_resp.text}"

        # Confirm authenticated session cookie (Django default is 'sessionid')
        assert "sessionid" in session.cookies, "No sessionid cookie set after login"

        # Step 3: Dispatch endpoint for role-based redirect
        # Get CSRF token from dispatch page or use existing
        dispatch_page_url = f"{BASE_URL}/accounts/dispatch/"
        csrf_token = get_csrf_token(session, dispatch_page_url)

        dispatch_url = f"{BASE_URL}/accounts/dispatch/"
        dispatch_headers = {
            "X-CSRFToken": csrf_token
        }
        dispatch_resp = session.post(dispatch_url, headers=dispatch_headers, timeout=TIMEOUT, allow_redirects=False)
        assert dispatch_resp.status_code in (302, 301), f"Expected redirect status code from dispatch, got {dispatch_resp.status_code}, content: {dispatch_resp.text}"
        location = dispatch_resp.headers.get("Location", "")
        assert location.endswith("/dashboard/teacher/"), f"Dispatch redirect did not lead to teacher dashboard, got: {location}"

    finally:
        # Cleanup: delete the created test user account
        try:
            logout_url = f"{BASE_URL}/accounts/logout/"
            session.post(logout_url, timeout=TIMEOUT)
        except Exception:
            pass

test_teacher_signup_login_and_role_dispatch()
