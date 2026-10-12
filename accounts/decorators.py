from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def role_required(role):
    def deco(view):
        @login_required
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.user.role != role and not request.user.is_superuser:
                return HttpResponseForbidden("This page is only available to %ss." % role)
            return view(request, *args, **kwargs)
        return wrapper
    return deco
