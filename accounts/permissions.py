# from rest_framework.permissions import BasePermission

# class IsAdmin(BasePermission):
#     """
#     Custom permission to allow only admin users to access user management views.
#     """
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.role == 'admin'

from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Custom permission to allow only admin users to access user management views.
    """
    def has_permission(self, request, view):
        # Ensure the user is authenticated and has an 'admin' role
        return request.user.is_authenticated and request.user.role == 'admin'

class IsOfficeStaff(BasePermission):
    """
    Custom permission to only allow Office Staff users to access certain views.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'office_staff'

class IsLibrarian(BasePermission):
    """
    Custom permission to only allow Librarian users to access certain views.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'librarian'
