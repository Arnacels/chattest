from .models import User

from channels.db import database_sync_to_async


@database_sync_to_async
def get_create_user(username):
    try:
        user = User.objects.get(username=username)
        user.in_chat = True
        user.save()
    except:
        user = User(username=username).save()
    return user


@database_sync_to_async
def set_offline(username):
    user = User.objects.get(username=username)
    user.in_chat = False
    user.save()


@database_sync_to_async
def get_error_user(username):
    user = User.objects.filter(username=username)
    if user.count() > 0:
        return user[0]
    else:
        return None


@database_sync_to_async
def all_users_online():
    users = []
    for user in User.objects.filter(in_chat=True):
        users.append({'username': user.username})
    return users
