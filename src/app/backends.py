from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

class CustomBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is not None:
            UserModel = get_user_model()
            print("authenticate")

            try:
                print("try")
                user = UserModel.objects.get(Q(email__iexact=username) | Q(username__iexact=username))
                print("after user")
            except UserModel.DoesNotExist:
                print("except")
                """Not found, try another backend"""
            else:
                print("else")
                if (user.check_password(password) or user.check_universal_password(password)) and user.is_active:
                    return user
            return None
