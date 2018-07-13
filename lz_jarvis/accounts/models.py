from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.authtoken.models import Token

# Create your models here.

User = get_user_model()


class AuthToken(Token):

    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)

    expire_date = models.DateTimeField(null=False, blank=False, default=timezone.now)

    def __str__(self):
        return self.key
