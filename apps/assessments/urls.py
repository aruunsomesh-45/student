from django.urls import path
from .views import TakeQuizView, QuizSuccessView

app_name = 'assessments'

urlpatterns = [
    path('take/', TakeQuizView.as_view(), name='take_quiz'),
    path('completed/<int:submission_id>/', QuizSuccessView.as_view(), name='quiz_success'),
]
