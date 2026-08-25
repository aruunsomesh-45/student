import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_student_dashboard_access_without_completed_assessment():
    session = requests.Session()
    try:
        # Step 1: Signup a new student without completed assessments
        signup_data = {
            "username": "teststudent_tc007",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
            "email": "teststudent_tc007@example.com",
            "first_name": "Test",
            "last_name": "Student",
            "academic_tier": "UG",
            "institution": "Test University"
        }
        signup_resp = session.post(f"{BASE_URL}/accounts/signup/student/", data=signup_data, timeout=TIMEOUT)
        assert signup_resp.status_code in (200, 201), f"Unexpected signup status: {signup_resp.status_code}"

        # Step 2: Login with the created student credentials
        login_data = {
            "username": signup_data["username"],
            "password": signup_data["password1"]
        }
        login_resp = session.post(f"{BASE_URL}/accounts/login/", data=login_data, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Unexpected login status: {login_resp.status_code}"

        # Step 3: Access /dashboard/student/results/ without completed assessment
        results_resp = session.get(f"{BASE_URL}/dashboard/student/results/", timeout=TIMEOUT, allow_redirects=False)
        assert results_resp.status_code in (200, 302), (
            f"Unexpected dashboard/results status code: {results_resp.status_code}")

        # If redirect (302), Location header should point to assessment page or an empty state page
        if results_resp.status_code == 302:
            location = results_resp.headers.get("Location", "")
            assert location, "Redirect location header missing"
            assert ("/assessments/take/" in location or "/dashboard/student/results/" in location or
                    "/dashboard/student/empty/" in location), f"Unexpected redirect location: {location}"
        else:
            # If 200, response should contain empty state guidance string
            # Since we don't know exact text, checking presence of typical empty state keywords
            empty_state_indicators = [
                "no completed assessments",
                "please take an assessment",
                "empty",
                "get started"
            ]
            content_lower = results_resp.text.lower()
            assert any(indicator in content_lower for indicator in empty_state_indicators), "Empty state guidance not detected"

        # Step 4: Attempt to GET /dashboard/student/pdf/ without assessment data
        pdf_resp = session.get(f"{BASE_URL}/dashboard/student/pdf/", timeout=TIMEOUT)
        assert pdf_resp.status_code in (400, 404), (
            f"Unexpected status code when fetching pdf without assessment: {pdf_resp.status_code}")

        # Response content should indicate report cannot be generated (check for keywords)
        error_indicators = [
            "cannot be generated",
            "no assessment data",
            "not found",
            "error",
            "missing"
        ]
        pdf_content_lower = pdf_resp.text.lower()
        assert any(indicator in pdf_content_lower for indicator in error_indicators), "Error message indicating no report not found"

    finally:
        # Cleanup: Delete the user to avoid clutter
        # Assuming we have an admin token or API to delete user by username (not specified in PRD)
        # Here, attempting to logout and delete if such endpoint existed (dummy code, no actual endpoint given)
        try:
            session.post(f"{BASE_URL}/accounts/logout/", timeout=TIMEOUT)
        except Exception:
            pass
        # If no user deletion endpoint, test user may persist; Normally would include cleanup here.


test_student_dashboard_access_without_completed_assessment()
