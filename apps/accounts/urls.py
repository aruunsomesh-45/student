from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    StudentSignUpView,
    TeacherSignUpView,
    RoleDispatchView,
    DemoLoginView,
    GoogleAuthInitView,
    GoogleSimulateCallbackView,
)

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('signup/student/', StudentSignUpView.as_view(), name='signup_student'),
    path('signup/teacher/', TeacherSignUpView.as_view(), name='signup_teacher'),
    path('dispatch/', RoleDispatchView.as_view(), name='dispatch'),
    path('demo/<str:role>/', DemoLoginView.as_view(), name='demo_login'),
    
    # Google OAuth helper & simulation endpoints
    path('google/init/', GoogleAuthInitView.as_view(), name='google_init'),
    path('google/callback/simulate/', GoogleSimulateCallbackView.as_view(), name='google_simulate_callback'),
]
