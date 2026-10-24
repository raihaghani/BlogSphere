from rest_framework.permissions import BasePermission, SAFE_METHODS
from blog.services import can_author, can_manage

class PostPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if view.action == 'comments':
            return request.user.is_authenticated
        if view.action == 'create':
            return can_author(request.user) or (request.user.is_staff and request.user.has_perm('blog.add_post'))
        return can_author(request.user) or (request.user.is_staff and request.user.has_perm(
            'blog.delete_post' if request.method == 'DELETE' else 'blog.change_post'))
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or view.action == 'comments':
            return obj.status == 'PUBLISHED'
        return can_manage(request.user, obj, 'delete' if request.method == 'DELETE' else 'change')

class CategoryPermission(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (request.user.is_staff and request.user.has_perm('blog.add_category'))
