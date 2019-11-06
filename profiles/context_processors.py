"""
Context processors to add variables to all templates.
"""

from django.conf import settings

def oauth2_enabled(request):
    """
    Adds variable OAUTH2_ENABLED to template if OAuth2 is configured in settings.py
    """
    return {
        'OAUTH2_ENABLED': settings.OAUTH2_ENABLED
    }
