from social_core.pipeline.user import create_user


def create_user_disabled(strategy, details, backend, user=None, *args, **kwargs):
    # Returns dict containing 'is_new' and 'user'
    result = create_user(strategy, details, backend, user, *args, **kwargs)

    if result['is_new']:
        django_user = result['user']
        django_user.is_active = False
        django_user.save()

    return result
