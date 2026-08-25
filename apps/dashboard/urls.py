from django.urls import path
from .views import (
    TeacherOverviewView,
    StudentDashboardView,
    StudentPlaybookView,
    DeleteTeacherNoteView,
    GenerateStudentAIPlanView,
    SaveTeacherLLMKeyView,
    GenerateCohortAISummaryView,
    StudentReportPDFView
)

app_name = 'dashboard'

urlpatterns = [
    path('student/results/', StudentDashboardView.as_view(), name='student_results'),
    path('student/results/<int:submission_id>/', StudentDashboardView.as_view(), name='student_results_detail'),
    path('submissions/<int:submission_id>/report/pdf/', StudentReportPDFView.as_view(), name='student_report_pdf'),
    
    # Teacher Dashboard & Playbook Routes
    path('teacher/', TeacherOverviewView.as_view(), name='teacher_overview'),
    path('teacher/students/<int:student_id>/playbook/', StudentPlaybookView.as_view(), name='student_playbook'),
    path('teacher/submissions/<int:submission_id>/playbook/', StudentPlaybookView.as_view(), name='submission_playbook'),
    path('teacher/notes/<int:note_id>/delete/', DeleteTeacherNoteView.as_view(), name='delete_teacher_note'),
    path('teacher/submissions/<int:submission_id>/ai-plan/', GenerateStudentAIPlanView.as_view(), name='student_ai_plan'),
    
    # Teacher AI Management
    path('teacher/ai/save-key/', SaveTeacherLLMKeyView.as_view(), name='save_llm_key'),
    path('teacher/ai/cohort-analysis/', GenerateCohortAISummaryView.as_view(), name='cohort_ai_analysis'),
]
