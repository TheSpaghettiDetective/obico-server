from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth import get_user_model

class CustomAuthenticationBackend(AuthenticationBackend):
    def authenticate(self, request, **credentials):
        UserModel = get_user_model()

        site = 2
        email = credentials.get("email")

        if email:
            user = UserModel.objects.filter(email=email, site=site).first()
            return user
        return None