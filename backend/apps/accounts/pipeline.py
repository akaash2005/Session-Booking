def save_avatar(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        avatar_url = response.get('picture')
    elif backend.name == 'github':
        avatar_url = response.get('avatar_url')
    else:
        avatar_url = None

    if avatar_url and not user.avatar:
        user.avatar = avatar_url
        user.save()