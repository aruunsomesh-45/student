import requests

BASE_URL = "http://localhost:8000"


def test_teacher_student_detail_and_mentoring_notes_persistence():
    timeout = 30
    session = requests.Session()

    def get_csrf_token(url):
        resp = session.get(url, timeout=timeout)
        resp.raise_for_status()
        return session.cookies.get("csrftoken")

    # -- Helper functions --
    def signup_teacher():
        url = f"{BASE_URL}/accounts/signup/teacher/"
        csrf_token = get_csrf_token(url)
        teacher_data = {
            "username": "testteacher_tc009",
            "password1": "StrongPass!123",
            "password2": "StrongPass!123",
            "email": "testteacher_tc009@example.com",
            "first_name": "Test",
            "last_name": "Teacher"
        }
        headers = {"X-CSRFToken": csrf_token, "Content-Type": "application/json"}
        resp = session.post(url, json=teacher_data, headers=headers, timeout=timeout)
        assert resp.status_code in (200, 201), f"Teacher signup failed: {resp.text}"

    def login_teacher():
        url = f"{BASE_URL}/accounts/login/"
        csrf_token = get_csrf_token(url)
        login_data = {
            "username": "testteacher_tc009",
            "password": "StrongPass!123"
        }
        headers = {"X-CSRFToken": csrf_token, "Content-Type": "application/json"}
        resp = session.post(url, json=login_data, headers=headers, timeout=timeout)
        assert resp.status_code == 200, f"Teacher login failed: {resp.text}"

    def signup_student():
        url = f"{BASE_URL}/accounts/signup/student/"
        csrf_token = get_csrf_token(url)
        student_data = {
            "username": "teststudent_tc009",
            "password1": "StrongPass!123",
            "password2": "StrongPass!123",
            "email": "teststudent_tc009@example.com",
            "first_name": "Test",
            "last_name": "Student",
            "academic_tier": "UG",
            "institution": "Test Institution"
        }
        headers = {"X-CSRFToken": csrf_token, "Content-Type": "application/json"}
        resp = session.post(url, json=student_data, headers=headers, timeout=timeout)
        assert resp.status_code in (200, 201), f"Student signup failed: {resp.text}"

    def login_student():
        url = f"{BASE_URL}/accounts/login/"
        csrf_token = get_csrf_token(url)
        login_data = {
            "username": "teststudent_tc009",
            "password": "StrongPass!123"
        }
        headers = {"X-CSRFToken": csrf_token, "Content-Type": "application/json"}
        resp = session.post(url, json=login_data, headers=headers, timeout=timeout)
        assert resp.status_code == 200, f"Student login failed: {resp.text}"

    def get_student_id():
        url = f"{BASE_URL}/dashboard/teacher/"
        resp = session.get(url, timeout=timeout)
        assert resp.status_code == 200, f"Teacher dashboard fetch failed: {resp.text}"
        data = resp.json()
        student_list = data.get("student_roster") or data.get("students") or []
        for student in student_list:
            if student.get("username") == "teststudent_tc009":
                return student.get("id") or student.get("student_id")
        return None

    def get_mentoring_notes(student_id):
        url = f"{BASE_URL}/dashboard/teacher/student/{student_id}/"
        resp = session.get(url, timeout=timeout)
        assert resp.status_code == 200, f"Failed to get student detail: {resp.text}"
        return resp.json()

    def update_mentoring_note(student_id, notes_payload):
        url = f"{BASE_URL}/dashboard/teacher/student/{student_id}/"
        csrf_token = get_csrf_token(url)
        headers = {"Content-Type": "application/json", "X-CSRFToken": csrf_token}
        resp = session.put(url, json=notes_payload, headers=headers, timeout=timeout)
        if resp.status_code not in (200, 302):
            resp = session.post(url, json=notes_payload, headers=headers, timeout=timeout)
        assert resp.status_code in (200, 302), f"Failed to update mentoring note: {resp.text}"

    def logout():
        url = f"{BASE_URL}/accounts/logout/"
        csrf_token = get_csrf_token(url)
        headers = {"X-CSRFToken": csrf_token}
        session.post(url, headers=headers, timeout=timeout)

    try:
        signup_teacher()
        login_teacher()

        signup_student()
        logout()
        login_teacher()

        student_id = get_student_id()
        assert student_id is not None, "Student ID not found in teacher dashboard."

        initial_data = get_mentoring_notes(student_id)
        initial_notes = initial_data.get("mentoring_notes") or ""

        updated_note_text = initial_notes + "\n[Automated test added note.]"
        update_payload = {"mentoring_notes": updated_note_text}
        update_mentoring_note(student_id, update_payload)

        post_update_data = get_mentoring_notes(student_id)
        post_update_notes = post_update_data.get("mentoring_notes") or ""
        assert updated_note_text == post_update_notes, "Mentoring notes update not persisted."

    finally:
        logout()


test_teacher_student_detail_and_mentoring_notes_persistence()
