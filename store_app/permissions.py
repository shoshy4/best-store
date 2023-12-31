from rest_framework import permissions

from store_app.models import Order

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class IsAdminPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and request.user.is_staff
        )


class IsOwnerOrAdminPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.customer == request.user or request.user.is_staff


class IsOwnerOfCartOrAdminPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        order = Order.objects.filter(pk=view.kwargs.get('pk'))
        return order[0].product_list__customer == request.user or request.user.is_staff

