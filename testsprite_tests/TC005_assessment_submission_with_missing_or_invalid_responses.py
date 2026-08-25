import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_assessment_submission_with_missing_or_invalid_responses():
    session = requests.Session()

    try:
        # Step 1: Authenticate a test student user (create if needed)
        signup_data = {
            "username": "teststudent_invalidresp",
            "password1": "Testpass123!",
            "password2": "Testpass123!",
            "email": "teststudent_invalidresp@example.com",
            "academic_tier": "UG",
            "institution": "Test University",
        }
        signup_resp = session.post(
            f"{BASE_URL}/accounts/signup/student/",
            json=signup_data,
            timeout=TIMEOUT,
        )
        if signup_resp.status_code not in (200, 201):
            # Possibly user exists or other issues, try login
            pass
        else:
            # Signup succeeded, continue
            pass

        # Step 2: Login with the test student credentials
        login_data = {
            "username": "teststudent_invalidresp",
            "password": "Testpass123!",
        }
        login_resp = session.post(
            f"{BASE_URL}/accounts/login/",
            data=login_data,
            timeout=TIMEOUT,
        )
        assert login_resp.status_code == 200, "Login failed for test student"

        # Step 3: Dispatch role to confirm student access and get session cookie
        dispatch_resp = session.post(
            f"{BASE_URL}/accounts/dispatch/",
            timeout=TIMEOUT,
            allow_redirects=False,
        )
        assert dispatch_resp.status_code in (302, 200), "Dispatch failed"
        location = dispatch_resp.headers.get("Location", "")
        assert "/assessments/take/" in location or location == "", "Unexpected dispatch redirect"

        # Step 4: Retrieve assessment questions for the student tier (UG assumed)
        get_assessment_resp = session.get(
            f"{BASE_URL}/assessments/take/",
            timeout=TIMEOUT,
        )
        assert get_assessment_resp.status_code == 200, "Failed to get assessment questions"
        assessment_questions = get_assessment_resp.json()

        # Build payload with missing or invalid responses
        answers_payload = {}
        questions = assessment_questions.get("questions") or assessment_questions.get("data") or []
        if not isinstance(questions, list):
            questions = []

        for q in questions:
            qid = q.get("id") or q.get("question_id") or None
            if qid is None:
                continue
            answers_payload[str(qid)] = ""  # empty string as invalid response

        # Step 5: Submit incomplete/invalid responses
        submit_resp = session.post(
            f"{BASE_URL}/assessments/take/",
            json={"responses": answers_payload},
            timeout=TIMEOUT,
        )
        assert submit_resp.status_code == 400, f"Expected 400 on invalid submission but got {submit_resp.status_code}"
        resp_json = None
        try:
            resp_json = submit_resp.json()
        except Exception:
            pass
        assert resp_json is not None, "Response is not JSON on validation error"

        # Validate presence of errors indicating missing or invalid responses
        error_fields = resp_json.get("errors") or resp_json.get("validation_errors") or resp_json.get("detail")
        assert error_fields, "No validation error details found in response"

        errors_text = str(error_fields).lower()
        assert (
            "incomplete" in errors_text or "invalid" in errors_text or "missing" in errors_text
        ), "Validation errors do not mention incomplete or invalid responses"

    finally:
        # Cleanup skipped as per instructions
        pass


test_assessment_submission_with_missing_or_invalid_responses()
