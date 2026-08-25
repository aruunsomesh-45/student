import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def get_csrf_token(session, url):
    resp = session.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    return session.cookies.get('csrftoken', '')

def test_student_signup_login_and_role_dispatch():
    session = requests.Session()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    try:
        # Get CSRF token for signup
        signup_url = f"{BASE_URL}/accounts/signup/student/"
        csrf_token = get_csrf_token(session, signup_url)
        signup_headers = headers.copy()
        signup_headers["X-CSRFToken"] = csrf_token

        # Step 1: Student Signup
        signup_payload = {
            "username": "teststudent123",
            "email": "teststudent123@example.com",
            "password": "StrongPass!123",
            "confirm_password": "StrongPass!123",
            "first_name": "Test",
            "last_name": "Student",
            "academic_tier": "UG",
            "institution": "Test University"
        }
        signup_resp = session.post(signup_url, json=signup_payload, headers=signup_headers, timeout=TIMEOUT)
        assert signup_resp.status_code in (200,201), f"Signup failed with status {signup_resp.status_code}, Response: {signup_resp.text}"

        # Get CSRF token for login
        login_url = f"{BASE_URL}/accounts/login/"
        csrf_token = get_csrf_token(session, login_url)
        login_headers = headers.copy()
        login_headers["X-CSRFToken"] = csrf_token

        # Step 2: Student Login
        login_payload = {
            "username": signup_payload["username"],
            "password": signup_payload["password"]
        }
        login_resp = session.post(login_url, json=login_payload, headers=login_headers, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}, Response: {login_resp.text}"

        # Confirm that session is authenticated by checking sessionid cookie
        session_cookie = session.cookies.get('sessionid')
        assert session_cookie, "Session cookie not set after login"

        # Get CSRF token for dispatch
        dispatch_url = f"{BASE_URL}/accounts/dispatch/"
        csrf_token = get_csrf_token(session, dispatch_url)
        dispatch_headers = {"Accept": "application/json", "X-CSRFToken": csrf_token}

        # Step 3: Role Dispatch
        dispatch_resp = session.post(dispatch_url, headers=dispatch_headers, timeout=TIMEOUT, allow_redirects=False)
        assert dispatch_resp.status_code in (200, 302), f"Dispatch returned unexpected status {dispatch_resp.status_code}"
        location = dispatch_resp.headers.get("Location", "")
        if dispatch_resp.status_code == 302:
            redirect_url = location
        else:
            # Avoid JSON decode errors by checking if content-type is JSON
            content_type = dispatch_resp.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                try:
                    resp_json = dispatch_resp.json()
                    redirect_url = resp_json.get("redirect_url") or resp_json.get("next") or ""
                except Exception:
                    redirect_url = ""
            else:
                redirect_url = ""
        assert redirect_url.startswith("/assessments/take") or redirect_url.startswith("/dashboard/student/results/"), \
            f"Dispatch redirect to unexpected URL: {redirect_url}"

    finally:
        # Cleanup is skipped as no delete endpoint specified
        pass

test_student_signup_login_and_role_dispatch()
