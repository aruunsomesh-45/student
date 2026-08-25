import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_student_assessment_submission_and_result_retrieval():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})

    # Obtain CSRF token by visiting login page (GET request)
    login_get_resp = session.get(f"{BASE_URL}/accounts/login/", timeout=TIMEOUT)
    assert login_get_resp.status_code == 200, f"Failed to GET login page: {login_get_resp.text}"

    # Extract CSRF token from cookies
    csrf_token = session.cookies.get('csrftoken')
    assert csrf_token, "CSRF token not found in cookies"

    # Include CSRF token in headers for POST request
    session.headers.update({"X-CSRFToken": csrf_token})

    # 1. Login as student (using test student credentials, assumed present)
    login_payload = {
        "username": "teststudent",
        "password": "TestPassword123!"
    }
    login_resp = session.post(f"{BASE_URL}/accounts/login/", json=login_payload, timeout=TIMEOUT)
    assert login_resp.status_code == 200, f"Student login failed: {login_resp.text}"

    # 2. Dispatch to confirm role-based redirect (optional, not strictly in test steps)
    dispatch_resp = session.post(f"{BASE_URL}/accounts/dispatch/", timeout=TIMEOUT)
    assert dispatch_resp.status_code in (200, 302), f"Dispatch failed: {dispatch_resp.text}"

    try:
        # 3. GET /assessments/take/ to get tier-specific questions
        get_assessment_resp = session.get(f"{BASE_URL}/assessments/take/", timeout=TIMEOUT)
        assert get_assessment_resp.status_code == 200, f"Failed to GET assessment questions: {get_assessment_resp.text}"

        # Check if response is JSON
        try:
            questions_data = get_assessment_resp.json()
        except Exception:
            assert False, f"Assessment questions response is not valid JSON: {get_assessment_resp.text}"

        # Ensure questions_data is dict and has 'questions' key with a list
        assert isinstance(questions_data, dict) and "questions" in questions_data and isinstance(questions_data["questions"], list), "Assessment questions missing or invalid format"

        questions_list = questions_data["questions"]

        # Prepare answers to submit
        answers_payload = {}

        for q in questions_list:
            qid = str(q.get("id") or q.get("question_id") or q.get("questionId"))
            if not qid:
                continue
            options = q.get("options") or q.get("choices") or []
            if options and isinstance(options, list) and len(options) > 0:
                first_opt = options[0]
                # first_opt can be dict or primitive
                if isinstance(first_opt, dict):
                    answer_val = first_opt.get("id") or first_opt.get("value") or first_opt
                else:
                    answer_val = first_opt
            else:
                # Use '1' as default answer if no options found
                answer_val = "1"
            answers_payload[qid] = answer_val

        # 4. Submit completed assessment answers via POST to /assessments/take/
        submit_resp = session.post(f"{BASE_URL}/assessments/take/", json=answers_payload, timeout=TIMEOUT, allow_redirects=False)
        assert submit_resp.status_code in (200, 302), f"Assessment submission failed: {submit_resp.text}"

        # Determine result_id
        result_id = None
        if submit_resp.status_code == 200:
            try:
                resp_json = submit_resp.json()
                for key in ('result_id', 'id', 'assessment_result_id', 'resultId'):
                    if key in resp_json:
                        result_id = resp_json[key]
                        break
            except Exception:
                pass
        elif submit_resp.status_code == 302:
            location = submit_resp.headers.get("Location", "")
            import re
            match = re.search(r"/assessments/completed/(\d+)/", location)
            if match:
                result_id = match.group(1)

        if not result_id:
            raise AssertionError("Could not find result_id from assessment submission response")

        # 5. GET /assessments/completed/<result_id>/ to retrieve detailed score breakdown
        completed_resp = session.get(f"{BASE_URL}/assessments/completed/{result_id}/", timeout=TIMEOUT)
        assert completed_resp.status_code == 200, f"Failed to GET completed assessment results: {completed_resp.text}"

        try:
            completed_data = completed_resp.json()
        except Exception:
            assert False, f"Completed assessment response is not valid JSON: {completed_resp.text}"

        expected_score_keys = [
            "growth_mindset",
            "learning_modality",
            "stress_response",
            "collaboration_orientation"
        ]

        # Require all keys to be present
        assert all(k in completed_data for k in expected_score_keys), "Score breakdown keys missing or invalid"

    finally:
        session.close()

test_student_assessment_submission_and_result_retrieval()
