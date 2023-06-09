import re
from typing import Union
from rest_framework import status
from django.contrib.auth import get_user_model
# local models
from .custom_classes import Error
from auth_profile.models import Profile
from auth_profile.schemas import MessageOut

User = get_user_model()


def password_validator(password: str) -> Union[str, None]:
    """
    This function validates the password,
    if the password is valid it returns None,
    if the password is not valid it returns a string message,.
    It should contain:
    - 8 characters long
    - one letter
    - one digit
    """
    if not len(password) >= 8:
        return 'Password is too short (8 characters minimum)'
    # define pattern for password validation 
    reg = "^(?=.*[A-Za-z])(?=.*\d).{8,}$"
    # compiling regex
    pattern = re.compile(reg)
    # searching regex
    is_match = re.search(pattern, password)
    # raising error if password is not valid
    if not is_match:
        return 'Password must be at least 8 characters long, and one letter, one number'

    return None


def get_user(email: str) -> Union[User, Error]:
    """
    - check if user exists
    - check if profile already exists
    . return profile if no error, 
    . return Error(http status, message dictionary) if error 404, or 400
    """
    try:
        # try to get user & profile
        user = User.objects.filter(email=email).select_related("profile_user").first()
        user.profile_user
    except AttributeError as e:
        # check if user not exists
        if e.args[0] == "'NoneType' object has no attribute 'profile_user'":
            # return (http status, message dictionary)
            return Error(status.HTTP_404_NOT_FOUND, MessageOut(detail="User not found"))
        # check if profile not exists
        if e.args[0] == "CustomUser has no profile_user.":
            # return (http status, message dictionary)
            return user
    return Error(status.HTTP_400_BAD_REQUEST, MessageOut(detail="Profile already exists"))

def get_user_profile(email: str) -> Union[Profile, Error]:
    """
    - check if user exists
    - check if profile exists
    . return profile if no error, 
    . return Error(http status, message dictionary) if error 404, or 400
    """
    try:
        # try to get user & profile
        user = User.objects.filter(email=email).select_related('profile_user').first()
        user_profile = user.profile_user
    except AttributeError as e:
        # check if user not exists
        if e.args[0] == "'NoneType' object has no attribute 'profile_user'":
            # return (http status, message dictionary)
            return Error(status.HTTP_404_NOT_FOUND, MessageOut(detail="User not found"))
        # check if profile not exists
        if e.args[0] == "CustomUser has no profile_user.":
            # return (http status, message dictionary)
            return Error(status.HTTP_404_NOT_FOUND, MessageOut(detail="Profile not found"))

        return Error(status.HTTP_400_BAD_REQUEST, MessageOut(detail=e.args[0]))
    return user_profile

def normalize_email(email: str) -> str:
    return email.strip().lower().replace(" ", "")
