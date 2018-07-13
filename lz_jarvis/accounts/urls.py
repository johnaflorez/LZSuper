from django.conf.urls import url

from accounts.views import auth_token_login, auth_token_logout

app_name = "accounts"

urlpatterns = [
    url(r'^login/$', auth_token_login, name='token_login'),
    url(r'^logout/$', auth_token_logout, name='token_logout')
]