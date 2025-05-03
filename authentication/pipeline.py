# authentication/pipeline.py
def save_profile_picture(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        picture_url = response.get('picture')
        if picture_url:
            user.profile_image_url = picture_url
            user.save()
