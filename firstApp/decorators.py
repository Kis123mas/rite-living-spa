from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages


def anonymous_required(view_func):
    """Prevent authenticated users from accessing the view, and stay on their current page."""
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in.")
            # Get the referring page
            referer = request.META.get('HTTP_REFERER')
            
            # Check if referer is available and not the same as the current page
            if referer and referer != request.build_absolute_uri():
                return redirect(referer)
            else:
                return redirect('landingpage')  # fallback if referer is invalid or same as current page
                
        return view_func(request, *args, **kwargs)
    return _wrapped_view



def admin_and_secretary_required(view_func):
    """Allow access only to users who are both admin and secretary."""
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.is_admin or request.user.is_secretary):
            return HttpResponseForbidden("You are not authorized to view this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view



def not_secretary_required(view_func):
    """Allow access only to users who are NOT a secretary."""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_not_secretary:
            return HttpResponseForbidden("You are not authorized to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view



def admin_required(view_func):
    """Allow access only to users who are admins."""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_admin:
            return HttpResponseForbidden("Only admins are allowed to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view