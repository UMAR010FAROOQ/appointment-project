# decorators.py
from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages

def simple_user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'simpleuserprofile'):
            return view_func(request, *args, **kwargs)
        else:
            messages.success(request, "You are not authorized to view this page. Login first.")
            return redirect('authentication:user-login')  # Replace with the appropriate login URL for simple users
    return _wrapped_view
