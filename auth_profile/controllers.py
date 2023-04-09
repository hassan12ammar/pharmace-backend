from typing import List
from ninja import Router
from rest_framework import status
from django.contrib.auth import get_user_model
from phonenumber_field.validators import validate_international_phonenumber
# local models
from .models import Profile
from basbos.utlize.custom_classes import Error
from auth_profile.authentication import CustomAuth, create_token
from basbos.utlize.utlize import get_user_profile, password_validator
from .schemas import AuthOut, MessageOut, ProfileIn, ProfileOut, SigninIn, UserIn


# Create your views here.
User = get_user_model()

auth_controller = Router()
profile_controller = Router()


""" Authentication End-points """


@auth_controller.post("signup", 
                      response={
                        201: AuthOut,
                        400: MessageOut,
                      }
)
def signup(request, acount_in: UserIn):
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
    email = acount_in.email.strip().lower().replace(" ", "")
    # check if email is already in use
    if User.objects.filter(email=acount_in.email).exists():
        return status.HTTP_400_BAD_REQUEST, MessageOut(detail="Email is already in use")
    # create user
    self_user = User.objects.create_user(
        # name=name,
        email=email,
        password=acount_in.password1
    )
    # create token for the user
    token = create_token(self_user)
    
    return status.HTTP_201_CREATED, AuthOut(token=token,
                                             user=self_user)


@auth_controller.post("signin", 
                      response={
                            200: AuthOut,
                            404: MessageOut,
                            400: MessageOut,
                      }
)
def signin(request, acount_in: SigninIn):
    # check if email exists
    is_user = User.objects.filter(email=acount_in.email).exists()
    if not is_user:
        return status.HTTP_404_NOT_FOUND, MessageOut(detail="User is not registered Or Email is wrong")
    # normalize email
    email = acount_in.email.strip().lower().replace(" ", "")
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
    email = request.auth

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
def create_profile(request, profile_in:ProfileIn):
    # get email from auth request
    email = request.auth

    # get the user instance
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
        img=profile_in.img,
        city=profile_in.city,
        state=profile_in.state,
        phone=profile_in.phone_number,
    )

    # save all changes
    profile.save()

    # create response
    project_dict = profile.__dict__
    project_dict["email"] = profile.user.email
    project_dict["img"] = str(project_dict["img"])
    project_dict["address"] = profile.address
    project_dict["phone_number"] = profile.phone_number

    profile_out = ProfileOut(**project_dict)

    return status.HTTP_200_OK, profile_out


@profile_controller.put("edit_profile",
                         response={200: ProfileOut, 
                                   404: MessageOut,
                                   400: MessageOut,
                                   },
                         auth=CustomAuth(),
)
def edit_profile(request, profile_in: ProfileIn):
    # get email from auth request
    email = request.auth

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
    profile.img = profile_in.img
    profile.city=profile_in.city
    profile.state=profile_in.state
    profile.phone=profile_in.phone_number

    # save all changes
    profile.save()

    return status.HTTP_200_OK, profile


