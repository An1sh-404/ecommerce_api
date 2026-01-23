from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow admins to edit objects, others can only read."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or request.user.is_admin
        )
    
class IsOwnerOrAdmin(permissions.BasePermission):
    """Custom permission to only allow owners of an object or admins to edit it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user.is_staff or request.user.is_admin:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        

        return False
    