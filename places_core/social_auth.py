# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from social.pipeline.partial import partial
from social.exceptions import AuthException


def create_auth_token(strategy, details, user=None, social=None, *args, **kwargs):
    """
    Tworzenie tokenu uwierzytalniającego dla aplikacji mobilnej.
    """
    from rest_framework.authtoken.models import Token
    token = None
    if user:
        try:
            token = user.auth_token
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)
            token.save()


def validate_email(strategy, details, user=None, social=None, *args, **kwargs):
    """
    Funkcja sprawdza, czy użytkownik o adresie email pobranym od dostawcy
    usługi uwierzytelniającej istnieje już w systemie. Jeżeli tak, konto
    social auth zostanie przypisane do tego użytkownika.
    """
    system_user = None
    try:
        system_user = User.objects.get(email=details.get('email'))
    except User.DoesNotExist:
        pass
    if user is None and system_user != None:
        return {'social': social,
                'user': system_user,
                'new_association': True}


@partial
def set_twitter_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    """
    Ustawienie adresu email dla użytkowników, którzy tworzą konto przez
    API Twittera.
    """
    if strategy.backend.name == 'twitter' and is_new:
        email = strategy.session_pop('account_email')
        if email:
            details['email'] = email
        else:
            return strategy.redirect(reverse('user:twitter_email'))