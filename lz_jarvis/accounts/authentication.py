from datetime import datetime, timedelta

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.utils import timezone

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ParseError

from accounts.models import AuthToken


class CustomTokenAuthentication(TokenAuthentication):

    def get_model(self):
        if self.model is not None:
            return self.model
        from accounts.models import AuthToken as Token
        return Token


class CustomTokenMiddleware(MiddlewareMixin):

    def process_request(self, request):
        try:
            token_key = request.META['HTTP_AUTHORIZATION'].split(' ')[1]
        except KeyError:
            pass
        except IndexError:
            raise ValueError("Token mal formed")
        else:
            try:
                token = AuthToken.objects.get(key=token_key)
            except AuthToken.DoesNotExist as e:
                raise ParseError(detail="Invalid Token")
            else:
                expire_date = token.expire_date.replace(tzinfo=None)
                if not expire_date > datetime.now():
                    token.delete()
                    raise ParseError(detail='Token Expired')
                elif hasattr(settings, 'TOKEN_EXPIRE_UPDATE_EVERY_REQUEST'):
                    if settings.TOKEN_EXPIRE_UPDATE_EVERY_REQUEST:
                        new_expire_date = timezone.now() + \
                                          timedelta(seconds=getattr(settings, 'REST_TOKEN_EXPIRE_SECONDS', None) or 300)
                        token.expire_date = new_expire_date
                        token.save()

