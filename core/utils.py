# core/utils.py

def is_organizer(user):
    return user.is_authenticated and user.role == 'organizer'