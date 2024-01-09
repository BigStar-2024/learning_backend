"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from users.admin import hidden_admin
from django.conf import settings
from django.conf.urls.static import static
from games.views import game_loader
from django.contrib.auth import views as auth_views
from . import views
from payments import views as paymentsViews
from django.views.static import serve
from django.conf.urls import url

from django.contrib import admin
from custom.admin import CustomAdmin

admin.site.__class__ = CustomAdmin

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^media/games/(?P<folder_name>.*)/gamePlay', game_loader),
    path('hidden-admin/', hidden_admin.urls),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=settings.DEBUG))),
    path('', csrf_exempt(GraphQLView.as_view(graphiql=settings.DEBUG))),
    path('stripe/', csrf_exempt(include("djstripe.urls", namespace="djstripe"))),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='emails/password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="emails/password/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='emails/password/password_reset_complete.html'), name='password_reset_complete'),
    path("password_reset/", views.password_reset_request, name="password_reset"),
    path("stripe-webhook/", paymentsViews.stripeWebHook, name="stripe_webhook"),
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]
