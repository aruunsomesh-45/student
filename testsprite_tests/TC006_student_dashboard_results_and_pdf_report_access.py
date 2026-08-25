import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def get_csrf_token(session, url):
    resp = session.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    if 'csrftoken' in session.cookies:
        return session.cookies['csrftoken']
    # fallback: try to extract csrf from cookies or response
    return ''

def test_student_dashboard_results_and_pdf_report_access():
    session = requests.Session()
    try:
        # --- Step 1: Login as an existing authenticated student with completed assessment ---
        # Signup new student - need CSRF token for POST
        signup_get_url = f"{BASE_URL}/accounts/signup/student/"
        csrf_token = get_csrf_token(session, signup_get_url)

        signup_data = {
            "username": "teststudent6",
            "password1": "StrongPass!234",
            "password2": "StrongPass!234",
            "email": "teststudent6@example.com",
            "tier": "UG",
            "institution": "Test University"
        }

        headers = {"X-CSRFToken": csrf_token} if csrf_token else {}

        signup_resp = session.post(f"{BASE_URL}/accounts/signup/student/", data=signup_data, headers=headers, timeout=TIMEOUT)
        assert signup_resp.status_code in (200, 201), f"Student signup failed: {signup_resp.status_code}, {signup_resp.text}"

        # Obtain CSRF token for login
        login_get_url = f"{BASE_URL}/accounts/login/"
        csrf_token = get_csrf_token(session, login_get_url)

        login_data = {
            "username": signup_data["username"],
            "password": signup_data["password1"]
        }

        headers = {"X-CSRFToken": csrf_token} if csrf_token else {}

        login_resp = session.post(f"{BASE_URL}/accounts/login/", data=login_data, headers=headers, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Student login failed: {login_resp.status_code}, {login_resp.text}"

        # Complete assessment first to have results to view

        # GET assessment questions
        get_assessment_resp = session.get(f"{BASE_URL}/assessments/take/", timeout=TIMEOUT)
        assert get_assessment_resp.status_code == 200, f"Failed to get assessment questions: {get_assessment_resp.status_code}, {get_assessment_resp.text}"
        questions = get_assessment_resp.json()
        assert isinstance(questions, dict), "Assessment questions response is not a JSON object"

        # Build completed answers payload based on questions keys (simulate valid answers)
        answers_payload = {}
        if "questions" in questions and isinstance(questions["questions"], list):
            for q in questions["questions"]:
                qid = str(q.get("id", ""))
                if qid:
                    answers_payload[qid] = "A"
        else:
            answers_payload = {"1": "A", "2": "B", "3": "C", "4": "D"}

        # Submit completed assessment
        # Also handle CSRF for this POST
        take_assessment_get_url = f"{BASE_URL}/assessments/take/"
        csrf_token = get_csrf_token(session, take_assessment_get_url)
        headers = {"X-CSRFToken": csrf_token} if csrf_token else {}

        submit_resp = session.post(f"{BASE_URL}/assessments/take/", json=answers_payload, headers=headers, timeout=TIMEOUT, allow_redirects=False)
        assert submit_resp.status_code in (200, 302), f"Assessment submission failed: {submit_resp.status_code}, {submit_resp.text}"

        result_id = None

        if submit_resp.status_code == 302:
            loc = submit_resp.headers.get("Location", "")
            if loc.startswith("/assessments/completed/"):
                try:
                    result_id = int(loc.split("/assessments/completed/")[1].rstrip("/"))
                except (IndexError, ValueError):
                    result_id = None

        if not result_id:
            test_result_id = 1
            resp = session.get(f"{BASE_URL}/assessments/completed/{test_result_id}/", timeout=TIMEOUT)
            if resp.status_code == 200:
                result_id = test_result_id

        assert result_id is not None, "Could not determine completed assessment result_id for student"

        # --- Step 2: GET /dashboard/student/results/ with authenticated student session ---
        dashboard_results_resp = session.get(f"{BASE_URL}/dashboard/student/results/", timeout=TIMEOUT)
        assert dashboard_results_resp.status_code == 200, f"Student dashboard results access failed: {dashboard_results_resp.status_code}, {dashboard_results_resp.text}"

        results_json = dashboard_results_resp.json()
        assert any(key in results_json for key in ["score_analytics", "personalized_playbook", "scores", "playbook", "results"]), "Dashboard results missing expected content"

        # --- Step 3: GET /dashboard/student/pdf/ to confirm downloadable PDF summary ---
        dashboard_pdf_resp = session.get(f"{BASE_URL}/dashboard/student/pdf/", timeout=TIMEOUT)
        assert dashboard_pdf_resp.status_code == 200, f"Student dashboard PDF report access failed: {dashboard_pdf_resp.status_code}, {dashboard_pdf_resp.text}"

        content_type = dashboard_pdf_resp.headers.get("Content-Type", "")
        content_disp = dashboard_pdf_resp.headers.get("Content-Disposition", "")
        assert "application/pdf" in content_type or "attachment" in content_disp, "PDF report response missing PDF content type or attachment disposition"

    finally:
        try:
            pass
        except Exception:
            pass

test_student_dashboard_results_and_pdf_report_access()
