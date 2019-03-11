"""
Module containing customisations to the Python Social Auth pipeline.

See https://python-social-auth.readthedocs.io/en/latest/
"""

from django.core.mail import mail_admins


from social_core.pipeline.user import create_user


def create_user_disabled(strategy, details, backend, user=None, *args, **kwargs):
    """
    Create a user account for the user being authenticated - but mark it as disabled.

    A new user must have their account enabled by an admin before they are able to log in.
    """
    # Returns dict containing 'is_new' and 'user'
    result = create_user(strategy, details, backend, user, *args, **kwargs)

    if result['is_new']:
        django_user = result['user']
        django_user.is_active = False
        django_user.save()

    return result


def email_admins(strategy, details, backend, user=None, *args, **kwargs):
    """
    Email the PEDASI admins if a new account has been created and requires approval
    """
    if kwargs['is_new']:
        mail_admins(
            subject='PEDASI Account Created',
            message=(
                'New PEDASI user account: {0}\n\n'
                'A new user account has been created by {1} - {2} and requires admin approval'
            ).format(
                user.username,
                user.get_full_name(),
                user.email
            )
        )
