from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrUsernameBackend(ModelBackend):
    """Lets people log in with either their username or their email."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        username = username or kwargs.get(User.USERNAME_FIELD)
        if not username or not password:
            return None
        try:
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            User().set_password(password)  # keep timing similar
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
