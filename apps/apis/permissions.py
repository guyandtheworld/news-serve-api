from django.contrib.auth.models import User

from rest_framework.permissions import BasePermission
from apis.models.users import DashUser

class IsAlrtAdmin(BasePermission):
    """
    Permission for alrt ai admins
    """
    message = "You must be an Alrt ai admin to access this"

    def has_permission(self, request, view):
        dash_user = DashUser.objects.get(user=request.user)
        
        if dash_user.user.is_staff and dash_user.role == "alrt-admin":
            return True
        else:
            return False


class IsAlrtSME(BasePermission):
    """
    Permission for alrt ai SME
    """
    message = "You must be an Alrt ai SME to access this"

    def has_permission(self, request, view):
        dash_user = DashUser.objects.get(user=request.user)
        
        return dash_user.role == "alrt-sme"


class IsAlrtTester(BasePermission):
    """
    Permission for alrt ai Tester
    """
    message = "You must be an Alrt ai QA to access this"

    def has_permission(self, request, view):
        dash_user = DashUser.objects.get(user=request.user)
        
        return dash_user.role == "alrt-qa"


class IsAlrtDemoUser(BasePermission):
    """
    Permission for alrt ai Demo user
    """

    def has_permission(self, request, view):
        dash_user = DashUser.objects.get(user=request.user)
        
        return dash_user.role == "demo-user"


class IsAlrtClientAdmin(BasePermission):
    """
    Permission for alrt ai Tester
    """

    def has_permission(self, request, view):
        dash_user = DashUser.objects.get(user=request.user)
        
        return dash_user.role == "client-admin"


class IsAlrtClientUser(BasePermission):
    """
    Permission for alrt ai Tester
    """

    def has_permission(self, request, view):
        dash_user = DashUser.objects.get(user=request.user)
        
        return dash_user.role == "client-user"