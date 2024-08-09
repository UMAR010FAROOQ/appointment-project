from django.shortcuts import redirect
from functools import wraps
from authentication import urls
from django.contrib import messages

def instructor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'instructorprofile'):
            return view_func(request, *args, **kwargs)
        else:
            messages.success(request, "You are not authorized to view this page. Login first.")
            return redirect('authentication:instructor-login')
    return _wrapped_view
