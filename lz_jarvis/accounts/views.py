from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

from rest_framework.viewsets import ViewSet
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken

from accounts.models import AuthToken

User = get_user_model()
# Create your views here.


class Login(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        sessions = AuthToken.objects.filter(user=user)
        if len(sessions) < 5:
            # Create a token each login request
            token = AuthToken.objects.create(user=user, expire_date=self._get_expire_time())
        else:
            raise exceptions.AuthenticationFailed(detail='You have maximum login session (5)')
        return Response({'token': token.key})

    @classmethod
    def _get_expire_time(cls):
        expire_time = timezone.now() + timedelta(seconds=getattr(settings, 'REST_TOKEN_EXPIRE_SECONDS', None) or 300)
        return expire_time


class Authentication(ViewSet):

    def logout(self, request, *args, **kwargs):
        if getattr(request.user, 'is_anonymous') and getattr(request, 'auth') is not None:
            raise exceptions.NotAuthenticated(detail='User not logged')
        else:
            token = request.auth
            try:
                AuthToken.objects.get(key=token.key)
            except Exception as e:
                raise exceptions.NotAuthenticated(detail=e)
            else:
                token.delete()
                return Response({'message': 'Logout successfully'})


auth_token_login = Login.as_view()

auth_token_logout = Authentication.as_view(
    {'get': 'logout'}
)
