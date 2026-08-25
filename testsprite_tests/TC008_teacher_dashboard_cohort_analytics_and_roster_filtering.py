import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def get_csrf_token(session, url):
    resp = session.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    return session.cookies.get('csrftoken', '')

def test_teacher_dashboard_cohort_analytics_and_roster_filtering():
    session = requests.Session()
    try:
        # Get CSRF token for signup
        csrf_token = get_csrf_token(session, f"{BASE_URL}/accounts/signup/teacher/")
        headers = {'X-CSRFToken': csrf_token}

        # Step 1: Register a new teacher (to get a fresh teacher account)
        teacher_signup_payload = {
            "username": "test_teacher_tc008",
            "email": "test_teacher_tc008@example.com",
            "password": "StrongPass!123",
            "first_name": "Test",
            "last_name": "Teacher"
        }
        signup_resp = session.post(f"{BASE_URL}/accounts/signup/teacher/", json=teacher_signup_payload, timeout=TIMEOUT, headers=headers)
        assert signup_resp.status_code in [200, 201], f"Teacher signup failed: {signup_resp.text}"

        # Get CSRF token for login
        csrf_token = get_csrf_token(session, f"{BASE_URL}/accounts/login/")
        headers = {'X-CSRFToken': csrf_token}

        # Step 2: Login with the registered teacher credentials
        login_payload = {
            "username": teacher_signup_payload["username"],
            "password": teacher_signup_payload["password"]
        }
        login_resp = session.post(f"{BASE_URL}/accounts/login/", json=login_payload, timeout=TIMEOUT, headers=headers)
        assert login_resp.status_code == 200, f"Teacher login failed: {login_resp.text}"

        # Get CSRF token for dispatch
        csrf_token = get_csrf_token(session, f"{BASE_URL}/accounts/dispatch/")
        headers = {'X-CSRFToken': csrf_token}

        # Step 3: Dispatch to confirm teacher role and session validity
        dispatch_resp = session.post(f"{BASE_URL}/accounts/dispatch/", timeout=TIMEOUT, allow_redirects=False, headers=headers)
        assert dispatch_resp.status_code in [302, 200], f"Dispatch failed: {dispatch_resp.text}"
        location = dispatch_resp.headers.get("Location", "")
        if dispatch_resp.status_code == 302:
            assert "/dashboard/teacher" in location, "Dispatch did not redirect to teacher dashboard"

        # Step 4: GET /dashboard/teacher/ without filters
        dashboard_resp = session.get(f"{BASE_URL}/dashboard/teacher/", timeout=TIMEOUT)
        assert dashboard_resp.status_code == 200, f"Teacher dashboard GET failed: {dashboard_resp.text}"
        data = dashboard_resp.json()
        # Validate expected keys exist (cohort analytics, roster, stress watchlist)
        assert "cohort_analytics" in data, "Missing cohort_analytics in response"
        assert "student_roster" in data, "Missing student_roster in response"
        assert "stress_watchlist" in data, "Missing stress_watchlist in response"

        # Extract some tiers and modalities from roster to apply filters
        roster = data.get("student_roster", [])
        if roster:
            available_tiers = list({student.get("tier") for student in roster if student.get("tier")})
            available_modalities = list({student.get("modality") for student in roster if student.get("modality")})
        else:
            available_tiers = []
            available_modalities = []

        # Prepare filters, fallback to a default if none found
        tier_filter = available_tiers[0] if available_tiers else "School"
        modality_filter = available_modalities[0] if available_modalities else "Visual"
        search_query = ""  # Empty search to just test filter narrowing

        # Step 5: GET /dashboard/teacher/ with search and filter params
        params = {
            "search": search_query,
            "tier": tier_filter,
            "modality": modality_filter
        }
        filtered_resp = session.get(f"{BASE_URL}/dashboard/teacher/", params=params, timeout=TIMEOUT)
        assert filtered_resp.status_code == 200, f"Filtered teacher dashboard GET failed: {filtered_resp.text}"
        filtered_data = filtered_resp.json()

        # Validate filtered keys exist and are consistent
        assert "student_roster" in filtered_data, "Missing student_roster in filtered response"
        assert "cohort_analytics" in filtered_data, "Missing cohort_analytics in filtered response"

        filtered_roster = filtered_data.get("student_roster", [])
        # Verify all returned students match the filter criteria
        for student in filtered_roster:
            assert student.get("tier") == tier_filter, f"Student tier mismatch: expected {tier_filter}, got {student.get('tier')}"
            assert student.get("modality") == modality_filter, f"Student modality mismatch: expected {modality_filter}, got {student.get('modality')}"

    finally:
        # Clean up - delete the created teacher account
        try:
            # Get CSRF token for delete
            csrf_token = get_csrf_token(session, f"{BASE_URL}/accounts/teacher/{teacher_signup_payload['username']}/")
            headers = {'X-CSRFToken': csrf_token}
            delete_resp = session.delete(f"{BASE_URL}/accounts/teacher/{teacher_signup_payload['username']}/", timeout=TIMEOUT, headers=headers)
            assert delete_resp.status_code in [200, 204], f"Teacher deletion failed: {delete_resp.text}"
        except Exception:
            pass

test_teacher_dashboard_cohort_analytics_and_roster_filtering()
