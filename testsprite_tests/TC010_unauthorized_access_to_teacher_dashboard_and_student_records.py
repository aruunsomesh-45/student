import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def get_csrf_token(session, url):
    resp = session.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    # Extract csrftoken cookie
    if "csrftoken" in session.cookies:
        return session.cookies["csrftoken"]
    # Fallback regex from HTML
    import re
    match = re.search(r"name='csrfmiddlewaretoken' value='(.+?)'", resp.text)
    if match:
        return match.group(1)
    else:
        raise ValueError("CSRF token not found")


def test_unauthorized_access_to_teacher_dashboard_and_student_records():
    session_student = requests.Session()
    session_no_auth = requests.Session()

    try:
        # Get CSRF token for student signup
        csrf_token = get_csrf_token(session_student, f"{BASE_URL}/accounts/signup/student/")

        # Signup student
        signup_data = {
            "username": "unauth_test_student",
            "password1": "TestPassword123!",
            "password2": "TestPassword123!",
            "email": "unauthstudent@example.com",
            "academic_tier": "UG",
            "institution": "Test University",
            "csrfmiddlewaretoken": csrf_token,
        }
        headers = {"Referer": f"{BASE_URL}/accounts/signup/student/"}
        resp = session_student.post(
            f"{BASE_URL}/accounts/signup/student/",
            data=signup_data,
            headers=headers,
            timeout=TIMEOUT,
        )
        assert resp.status_code in (200, 201), f"Student signup failed: {resp.status_code} {resp.text}"

        # Get CSRF token for student login
        csrf_token = get_csrf_token(session_student, f"{BASE_URL}/accounts/login/")

        # Login student
        login_data = {
            "username": signup_data["username"],
            "password": signup_data["password1"],
            "csrfmiddlewaretoken": csrf_token,
        }
        headers = {"Referer": f"{BASE_URL}/accounts/login/"}
        resp = session_student.post(
            f"{BASE_URL}/accounts/login/",
            data=login_data,
            headers=headers,
            timeout=TIMEOUT,
        )
        assert resp.status_code == 200, f"Student login failed: {resp.status_code} {resp.text}"

        # Get CSRF token for dispatch
        csrf_token = get_csrf_token(session_student, f"{BASE_URL}/accounts/dispatch/")

        # Dispatch to set the session properly (student)
        headers = {"Referer": f"{BASE_URL}/accounts/dispatch/"}
        resp = session_student.post(
            f"{BASE_URL}/accounts/dispatch/",
            data={"csrfmiddlewaretoken": csrf_token},
            headers=headers,
            allow_redirects=False,
            timeout=TIMEOUT,
        )
        # Expect redirect to student area (/assessments/take/ or /dashboard/student/results/)
        assert resp.status_code in (302, 200), "Student dispatch failed"

        # 2) Attempt GET /dashboard/teacher/ with student session (should be denied)
        resp = session_student.get(
            f"{BASE_URL}/dashboard/teacher/",
            allow_redirects=False,
            timeout=TIMEOUT,
        )
        assert resp.status_code in (302, 401, 403), (
            f"Access to teacher dashboard with student session should be denied but got {resp.status_code}"
        )

        # 3) Attempt GET /dashboard/teacher/ without authentication (no auth session)
        resp = session_no_auth.get(
            f"{BASE_URL}/dashboard/teacher/",
            allow_redirects=False,
            timeout=TIMEOUT,
        )
        assert resp.status_code in (302, 401, 403), (
            f"Access to teacher dashboard without authentication should be denied but got {resp.status_code}"
        )

        # 4) Create another student to test access to student records via teacher route without teacher auth
        csrf_token = get_csrf_token(session_student, f"{BASE_URL}/accounts/signup/student/")
        resp = session_student.post(
            f"{BASE_URL}/accounts/signup/student/",
            data={
                "username": "unauth_test_student2",
                "password1": "TestPassword123!",
                "password2": "TestPassword123!",
                "email": "unauthstudent2@example.com",
                "academic_tier": "UG",
                "institution": "Test University",
                "csrfmiddlewaretoken": csrf_token,
            },
            headers={"Referer": f"{BASE_URL}/accounts/signup/student/"},
            timeout=TIMEOUT,
        )
        assert resp.status_code in (200,201), f"Second student signup failed: {resp.status_code} {resp.text}"

        # For the sake of test, attempt access with typical id 9999999 (nonexistent student)
        nonexistent_student_id = 9999999

        # 5) Attempt GET /dashboard/teacher/student/<student_id>/ without teacher authorization
        # Use no auth session first
        resp = session_no_auth.get(
            f"{BASE_URL}/dashboard/teacher/student/{nonexistent_student_id}/",
            allow_redirects=False,
            timeout=TIMEOUT,
        )
        assert resp.status_code in (302, 401, 403, 404), (
            f"Access to teacher-student detail without auth should be denied or 404 but got {resp.status_code}"
        )

        # Now with student session but different student ID should be denied access
        resp = session_student.get(
            f"{BASE_URL}/dashboard/teacher/student/{nonexistent_student_id}/",
            allow_redirects=False,
            timeout=TIMEOUT,
        )
        assert resp.status_code in (403, 404), (
            f"Access to another student's record with student session should be denied but got {resp.status_code}"
        )

    finally:
        # No cleanup available as per PRD
        pass


test_unauthorized_access_to_teacher_dashboard_and_student_records()
