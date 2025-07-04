from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return str(obj.sold_by).strip() == str(request.user.uid).strip()


