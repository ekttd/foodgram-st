from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAuthenticatedOrReadOnly)


class AdminOrReadOnly(BasePermission):
    """Разрешение на создание и изменение только для админов."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_staff
        )


class IsOwnerOrReadOnly(IsAuthenticatedOrReadOnly):
    """Разрешение на создание и изменение только для автора или админа."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user == obj.author
            or request.user.is_staff
        )
