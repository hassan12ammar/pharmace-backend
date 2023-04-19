from PIL import Image
from typing import List
from rest_framework import status
from ninja import Router, UploadedFile
from auth_profile.models import Profile
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
# locall models
from .models import Cart, DrugItem, Pharmacy, Review, Drug
from pharmace.utlize.custom_classes import Error
from auth_profile.authentication import CustomAuth
from pharmace.utlize.utlize import get_user_profile, normalize_email
from .schemas import (CartOut, DrugItemOut, PharmacyOut, 
                      PharmacyShort, MessageOut, ReviewIn, ReviewOut, SeedSchema)
User = get_user_model()

# 
pharmacy_router = Router()
cart_router = Router()
draft_router = Router()

""" Pharmacy """


@pharmacy_router.get("get_all/{page_number}",
                     response={
                         200:List[PharmacyShort],
                     })
def get_all(request, page_number: int):
    pharmacies = Pharmacy.objects.all().order_by('id')
    # Set the number of objects per page
    paginator = Paginator(list(pharmacies), 6)

    page_obj = paginator.get_page(page_number)

    serialized_data = [pharmacy 
                       for pharmacy in page_obj]

    return status.HTTP_200_OK, serialized_data


@pharmacy_router.get("get_by_id/{id}",
                     response={
                         200:List[PharmacyOut],
                         400: MessageOut
                     })
def get_by_id(request, id: int):
    pharmacy = Pharmacy.objects.filter(id=id)
    if not pharmacy:
        return status.HTTP_400_BAD_REQUEST, MessageOut(detail=f"Pharmacy with id {id} Not Found")

    return status.HTTP_200_OK, Pharmacy.objects.filter(id=id)


@pharmacy_router.get("get_reviews/{id}",
                     response={
                         200:List[ReviewOut],
                         400: MessageOut,
                     },)
def get_pharm_reviews(request, id: int):
    pharmacy = Pharmacy.objects.filter(id=id).first()
    if not pharmacy:
        return status.HTTP_400_BAD_REQUEST, MessageOut(detail=f"Pharmacy with id {id} Not Found")

    return Review.objects.filter(pharmacy=pharmacy)


@pharmacy_router.get("search_pharmacy/{name}",
                     response={200: List[PharmacyShort],
                               400: MessageOut,},)
def search_location(request, name: str):
    return status.HTTP_200_OK, Pharmacy.objects.filter(name__contains=name)


@pharmacy_router.get("search_by_location/{location}",
                     response={200: List[PharmacyShort],
                               400: MessageOut,},)
def search_location(request, location: str):
    return status.HTTP_200_OK, Pharmacy.objects.filter(location__contains=location)


@pharmacy_router.get("filter_by_rates/{name}",
                     response={200: List[PharmacyShort],
                               400: MessageOut,},)
def filter_rates(request, name: str):
    pharmacies = Pharmacy.objects.filter(name__contains=name).order_by("-review__rating")

    return status.HTTP_200_OK, pharmacies


@pharmacy_router.get("filter_by_location/{name}",
                     response={200: List[PharmacyShort],
                               400: MessageOut,},
                     auth=CustomAuth(),)
def filter_location(request, name: str):
    # get the user from email in auth
    email = normalize_email(request.auth)

    # get user profile
    profile = get_user_profile(email)
    if isinstance(profile, Error):
        return profile.status, profile.message

    pharmacy = Pharmacy.objects.filter(name__contains=name).filter(location__contains=profile.province)

    return status.HTTP_200_OK, pharmacy


@pharmacy_router.post("add_edit_review",
                      response={200: ReviewOut,
                                400: MessageOut,
                                404: MessageOut},
                      auth=CustomAuth(),)
def add_edit_review(request, review_in: ReviewIn):
    # get the user from email in auth
    email = normalize_email(request.auth)

    # get user profile
    profile = get_user_profile(email)
    if isinstance(profile, Error):
        return profile.status, profile.message

    pharmacy = Pharmacy.objects.filter(id=review_in.Pharmacy_id).first()
    # get the review or create new one

    review, _ = Review.objects.get_or_create(user=profile, pharmacy=pharmacy,
                                             defaults={'rating': 0, 'description': ''})
    review.rating = review_in.rating
    review.description = review_in.description

    review.save()

    return review


@pharmacy_router.delete("delet_review/{pharmacy_id}",
                        response={200: MessageOut,
                                  404: MessageOut,},
                        auth=CustomAuth(),)
def delete_review(request, pharmacy_id: int):
    # get the user from email in auth
    email = normalize_email(request.auth)

    # get user profile
    profile = get_user_profile(email)
    if isinstance(profile, Error):
        return profile.status, profile.message
  
    review = Review.objects.filter(user=profile, pharmacy = pharmacy_id)
    if not review.exists():
        return status.HTTP_404_NOT_FOUND, MessageOut(detail="Review Not Found")

    review.delete()
    return status.HTTP_200_OK, MessageOut(detail="Review Deleted Successfully")


""" Cart """


@cart_router.get("get_cart",
                 response={200:CartOut},
                 auth=CustomAuth(),)
def get_cart(request):
    # get the user from email in auth
    email = normalize_email(request.auth)

    # get user profile
    profile = get_user_profile(email)
    if isinstance(profile, Error):
        return profile.status, profile.message

    cart = Cart.objects.filter(user=profile).first()
    items = list(DrugItem.objects.filter(cart=cart))
    total =  sum([
            item.drug.price * item.amount
            for item in items
            ])
    
    # get shipping cost
    shipping = items[0].drug.pharmacy.shipping

    result = cart.__dict__
    result["items"] = items
    result["user"] = profile
    result["total"] = total
    result["shipping"] = shipping

    return status.HTTP_200_OK, result


@cart_router.post("add_increment_to_cart/{drug_id}",
                  response={
                      200: DrugItemOut,
                      400: MessageOut,
                      404: MessageOut,
                  },
                auth=CustomAuth(),)
def add_to_cart(request, drug_id: int):
    # get the user from email in auth
    email = normalize_email(request.auth)

    # check if user and profile exists
    profile = get_user_profile(email)
    if isinstance(profile, Error):
        return profile.status, profile.message
    # cart of the user
    cart = Cart.objects.filter(user=profile).first()
    drug = Drug.objects.filter(id=drug_id).first()

    # check if there is an item
    item = DrugItem.objects.filter(drug=drug,
                                   cart=cart,)

    if item.exists():
        item = item.first()
        item.amount += 1
        item.save()

        return item
    
    # create Item
    item = DrugItem.objects.create(drug = drug,
                                          cart=cart,
                                          amount=1)

    return item


@cart_router.put("decrease_from_cart/{drug_id}",
                  response={
                      200: DrugItemOut,
                      400: MessageOut,
                      404: MessageOut,
                  },
                auth=CustomAuth(),)
def decrease_from_cart(request, drug_id: int):
    # get the user from email in auth
    email = normalize_email(request.auth)

    # check if user and profile exists
    profile = get_user_profile(email)
    if isinstance(profile, Error):
        return profile.status, profile.message

    # cart of the user
    cart = Cart.objects.filter(user=profile).first()
    drug = Drug.objects.filter(id=drug_id).first()

    # check if there is an item
    item = DrugItem.objects.filter(drug=drug,
                                   cart=cart,)

    if item.exists():
        item = item.first()
        item.amount -= 1
        item.save()

        if item.amount <= 0:
            item.delete()
            return status.HTTP_200_OK, MessageOut(detail="Item Deleted")

        return item

    return status.HTTP_404_NOT_FOUND, MessageOut(detail="Item Not Found")


""" Draft """


@draft_router.post("create_seed", response={200: SeedSchema})
def create(request):
    """
    make sure you have these files:
        - seed_img/drug.png
        - seed_img/pharmacy.jpg
        - seed_img/profile.png
    """

    pharmacy_img = "seed_img/pharmacy.jpg"

    pharmacies = []
    for i in range(10):
        pharmacy, _ = Pharmacy.objects.get_or_create(
                name=f"{i} Nahr",
                description="A family-owned pharmacy that has been serving the community",
                location="Al Mansour / alroad / cross meshmesha",
                img=pharmacy_img,
        )

        pharmacies.append(pharmacy)


    drug_img = "seed_img/drug.png"

    for pharmacy_ in range(len(pharmacies)):
        for drug_ in range(10):
            Drug.objects.get_or_create(
                name = f"{drug_} Ibuprofen 200mg tablets",
                description ="Pain relief for headaches, toothaches, menstrual cramps, and other minor aches and pains.",
                img = drug_img,
                price=4.99,
                is_active=True,
                pharmacy=pharmacies[pharmacy_],
            )

    user, _ = User.objects.get_or_create(
        email= 'user1@example.com',
        password= 'String1@',
    )

    profile_img = "seed_img/profile.png"

    profile, _ = Profile.objects.get_or_create(
        user=user, 
        name='BASBOS',
        img=profile_img
    )

    return status.HTTP_200_OK, SeedSchema(
        pharmacies= pharmacies,
        profile= profile
        )


@draft_router.put("remove_from_cart/{drug_id}",
                  response={
                      200: DrugItemOut,
                      400: MessageOut,
                      404: MessageOut,
                  },
                auth=CustomAuth(),)
def remove_from_cart(request, drug_id: int):
    # get the user from email in auth
    email = normalize_email(request.auth)

    # check if user and profile exists
    profile = get_user_profile(email)
    if isinstance(profile, Error):
        return profile.status, profile.message

    # cart of the user
    cart = Cart.objects.filter(user=profile).first()
    drug = Drug.objects.filter(id=drug_id).first()

    # check if there is an item
    item = DrugItem.objects.filter(drug=drug,
                                   cart=cart,)

    if item.exists():
        item = item.first()
        item.delete()

        return status.HTTP_200_OK, MessageOut(detail="Item Deleted")

    return status.HTTP_404_NOT_FOUND, MessageOut(detail="Item Not Found")

