from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def teacher_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_teacher_user():
            messages.warning(request, "Access restricted. Only verified teachers can access this dashboard.")
            return redirect('accounts:dispatch')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_student_user():
            messages.warning(request, "Access restricted to students.")
            return redirect('accounts:dispatch')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
