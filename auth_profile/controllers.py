import os
from uuid import uuid4
from typing import List
from rest_framework import status
from ninja import Body, File, Router, UploadedFile
from django.contrib.auth import get_user_model
from phonenumber_field.validators import validate_international_phonenumber
# local models
from .models import Profile
from core.models import Cart
from pharmace.utlize.custom_classes import Error
from auth_profile.authentication import CustomAuth, create_token
from pharmace.utlize.utlize import get_user_profile, password_validator, normalize_email
from .schemas import AuthOut, MessageOut, ProfileIn, ProfileOut, SigninIn, SigninUpIn, SigninUpOut


# Create your views here.
User = get_user_model()

auth_controller = Router()
profile_controller = Router()


""" Authentication End-points """


@auth_controller.post("signup", 
                      response={
                        201: SigninUpOut,
                        400: MessageOut,
                      }
)
def signup(request, acount_in: SigninUpIn):
    """
    passwor must contain at least:
    - 8 characters long
    - one letter
    - one digit
    """
    # validadte password
    error_message = password_validator(acount_in.password1)
    if error_message:
        return status.HTTP_400_BAD_REQUEST, {"detail": error_message}
    # check if password1 and password2 are the same
    if acount_in.password1 != acount_in.password2:
        return status.HTTP_400_BAD_REQUEST, MessageOut(detail="passwords do not match")
    # normalize the data
    email = normalize_email(acount_in.email)
    # check if email is already in use
    if User.objects.filter(email=acount_in.email).exists():
        return status.HTTP_400_BAD_REQUEST, MessageOut(detail="Email is already in use")
    # create user
    user = User.objects.create_user(
        # name=name,
        email=email,
        password=acount_in.password1
    )
    # create empty profile with just name and user
    profile = Profile.objects.create(user=user, 
                           name=acount_in.name)
    # create token for the user
    token = create_token(user)

    return status.HTTP_201_CREATED, SigninUpOut(token=token,
                                                 user=user,
                                                 name=profile.name)


@auth_controller.post("signin", 
                      response={
                            200: AuthOut,
                            404: MessageOut,
                            400: MessageOut,
                      }
)
def signin(request, acount_in: SigninIn):
    # normalize email
    email = normalize_email(acount_in.email)
    # check if email exists
    is_user = User.objects.filter(email=email).exists()
    if not is_user:
        return status.HTTP_404_NOT_FOUND, MessageOut(detail="User is not registered Or Email is wrong")

    # check if password is correct
    user = User.objects.get(email=email)
    if user.check_password(acount_in.password):
        # create token for user
        token = create_token(user)
        return status.HTTP_200_OK, AuthOut(token=token, user=user)

    return status.HTTP_400_BAD_REQUEST, MessageOut(detail="Wrong password")



""" Profile End-points """


@profile_controller.get("get_all_profile", response={200: List[ProfileOut],},)
def all_profile(request):
    return status.HTTP_200_OK, Profile.objects.all().select_related('user')



@profile_controller.get("get_profile", 
                        response={
                            200: ProfileOut, 
                            404: MessageOut,
                            400:MessageOut,
                            },
                        auth=CustomAuth(),
)
def get_profile(request):
    # get email from auth request
    email = normalize_email(request.auth)

    # check if user and profile exists
    profile = get_user_profile(email)
    if isinstance(profile, Error):
        return profile.status, profile.message

    return status.HTTP_200_OK, profile


@profile_controller.post("create_profile",
                         response={200: ProfileOut, 
                                   404: MessageOut,
                                   400: MessageOut,
                                   },
                        auth=CustomAuth(),
)
def create_profile(request, profile_in: ProfileIn, img: UploadedFile=None):
    # get email from auth request
    email = normalize_email(request.auth)

    # get the user iAttributeError: _committednstance
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return status.HTTP_404_NOT_FOUND, MessageOut(detail="User not found.")

    profile_exists = Profile.objects.filter(user=user).exists()
    if profile_exists:
        return status.HTTP_404_NOT_FOUND, MessageOut(detail="Profile alrady exists.")

    # validate phone number
    try:
        validate_international_phonenumber(profile_in.phone_number)
    except:
        return status.HTTP_400_BAD_REQUEST, MessageOut(detail="phone number is not valid.")

    # create the profile
    profile = Profile.objects.create(
        user=user,
        name=profile_in.name,
        city=profile_in.city,
        province=profile_in.province,
        phone=profile_in.phone_number,
    )

    # Save profile picture
    if img:
        profile.img.save(f'profile-{profile.id}-{uuid4()}.jpg', img)
    else: profile.img=img

    # save all changes
    profile.save()

    # create empty Cart for the user
    Cart.objects.create(user=profile)

    # create response
    project_dict = profile.__dict__
    project_dict["email"] = profile.user.email
    project_dict["img"] = str(project_dict["img"])
    project_dict["city"] = profile.city
    project_dict["province"] = profile.province
    project_dict["phone_number"] = profile.phone_number

    profile_out = ProfileOut(**project_dict)

    return status.HTTP_200_OK, profile_out


@profile_controller.post("edit_profile",
                         response={200: ProfileOut, 
                                   404: MessageOut,
                                   400: MessageOut,
                                   },
                         auth=CustomAuth(),
)
def edit_profile(request, profile_in: ProfileIn=Body(...), img: UploadedFile=File(None)):
    # get email from auth request
    email = normalize_email(request.auth)

    # Check if user profile exists
    profile = get_user_profile(email)
    if isinstance(profile, Error):
        return profile.status, profile.message

    # validate phone number
    try:
        validate_international_phonenumber(profile_in.phone_number)
    except:
        return status.HTTP_400_BAD_REQUEST, MessageOut(detail="phone number is not valid.")

    # Update the user profile
    profile.name = profile_in.name
    profile.city=profile_in.city
    profile.province=profile_in.province
    profile.phone=profile_in.phone_number

    # Save new profile picture if provided
    if img:
        # remove old img
        if profile.img:
            os.remove(profile.img.path)
        # profile.img = img
        profile.img.save(f'profile-{profile.id}-{uuid4()}.jpg', img)

    # save all changes
    profile.save()

    return status.HTTP_200_OK, profile


