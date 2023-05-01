import random
from typing import List
from ninja import Router
from rest_framework import status
from django.db.models import Avg, Q
from auth_profile.models import Profile
from django.contrib.auth import get_user_model
from pharmace.utlize.constant import (DRUG_PER_PAGE, PHARMACY_PER_PAGE, 
                                      REVIEW_DESCRIPTION, REVIEW_PER_PAGE)
# locall models
from .models import Cart, DrugItem, OpeningHours, Pharmacy, Review, Drug
from pharmace.utlize.custom_classes import Error
from auth_profile.authentication import CustomAuth
from pharmace.utlize.utlize import get_user_profile, normalize_email
from .schemas import (CartOut, Checkout, DrugOut, ItemUpdate, PharmacyOut, 
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
                         400: MessageOut
                     })
def get_all(request, page_number: int):
    # validate page number
    if page_number <= 0:
        return status.HTTP_400_BAD_REQUEST, MessageOut(
                detail="Invalid page number Has to be grater than 0")

    start = (page_number - 1) * PHARMACY_PER_PAGE
    end = start + PHARMACY_PER_PAGE

    pharmacies = Pharmacy.objects.order_by('id')[start:end]

    return status.HTTP_200_OK, list(pharmacies)


@pharmacy_router.get("get_by_id/{id}",
                     response={
                         200:PharmacyOut,
                         400: MessageOut
                     })
def get_by_id(request, id: int):
    pharmacy = Pharmacy.objects.filter(id=id)
    if not pharmacy:
        return status.HTTP_400_BAD_REQUEST, MessageOut(detail=f"Pharmacy with id {id} Not Found")

    return status.HTTP_200_OK, Pharmacy.objects.filter(id=id).first()


@pharmacy_router.get("get_druge/{pharmacy_id}/{page_number}",
                     response={
                         200:List[DrugOut],
                         400: MessageOut
                     })
def get_druge(request, pharmacy_id: int, page_number: int):
    # validate page number
    if page_number <= 0:
        return status.HTTP_400_BAD_REQUEST, MessageOut(
                detail="Invalid page number Has to be grater than 0")

    start = (page_number - 1) * DRUG_PER_PAGE
    end = start + DRUG_PER_PAGE

    drugs = Drug.objects.filter(pharmacy=pharmacy_id)[start:end]

    if not drugs:
        return (status.HTTP_400_BAD_REQUEST, 
                MessageOut(detail=f"No Drugs with id {pharmacy_id}"))

    return status.HTTP_200_OK, drugs


@pharmacy_router.get("get_reviews/{id}",
                     response={
                         200:List[ReviewOut],
                         400: MessageOut,
                     },)
def get_pharm_reviews(request, id: int, page_number: int=1):
    pharmacy = Pharmacy.objects.filter(id=id).first()
    if not pharmacy:
        return status.HTTP_400_BAD_REQUEST, MessageOut(detail=f"Pharmacy with id {id} Not Found")

    start = (page_number - 1) * REVIEW_PER_PAGE
    end = start + REVIEW_PER_PAGE

    return Review.objects.filter(pharmacy=pharmacy).order_by("-id")[start:end]


@pharmacy_router.get("search_pharmacy/{drug_name}",
                     response={200: List[PharmacyShort],
                               400: MessageOut,},)
def search_name(request, drug_name: str):
    return status.HTTP_200_OK, Pharmacy.objects.filter(drug__name__icontains=drug_name).distinct()


@pharmacy_router.get("search_by_location/{drug_name}",
                     response={200: List[PharmacyShort],
                               400: MessageOut,},
                     auth=CustomAuth())
def search_location(request, drug_name: str):
    email = normalize_email(request.auth)
    # get user profile
    profile = get_user_profile(email)
    if isinstance(profile, Error):
        return profile.status, profile.message
    pharmacies = (Pharmacy.objects
                  .filter(drug__name__icontains=drug_name)
                  .distinct()
                  .filter(
                      Q(location__icontains=profile.city) |
                      Q(location__icontains=profile.province)
                      )
                  )

    return status.HTTP_200_OK, pharmacies


@pharmacy_router.get("filter_by_rates/{drug_name}",
                     response={200: List[PharmacyShort],
                               400: MessageOut,},)
def filter_rates(request, drug_name: str):
    pharmacies = (Pharmacy.objects.filter(drug__name__icontains=drug_name)
                  .distinct()
                  .annotate(rate_avg=Avg("review__rating"))
                  .order_by("rate_avg"))

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

    pharmacy = Pharmacy.objects.filter(name__icontains=name).filter(location__icontains=profile.province)

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

    return status.HTTP_200_OK, cart


@cart_router.post("add_increment_to_cart/{drug_id}",
                  response={
                      200: ItemUpdate,
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
                      200: ItemUpdate,
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

    if not item.exists():
        return status.HTTP_404_NOT_FOUND, MessageOut(detail="Item Not Found")

    item = item.first()
    item.amount -= 1
    item.save()

    if item.amount <= 0:
        item.delete()
        item

    return status.HTTP_200_OK, item


@cart_router.put("checkout",
                  response={
                      200: Checkout,
                      400: MessageOut,
                  },
                auth=CustomAuth(),)
def checkout(request):
    # get the user from email in auth
    email = normalize_email(request.auth)

    # get user profile
    profile = get_user_profile(email)
    if isinstance(profile, Error):
        return profile.status, profile.message

    cart = Cart.objects.filter(user=profile).first()
    # Serialize the old cart data
    old_cart = Checkout.from_orm(cart)

    for item in cart.items:
        item.delete()

    return status.HTTP_200_OK, old_cart


""" Draft """


@draft_router.post("create_seed", response={200: SeedSchema})
def create(request):
    """
    make sure you have these files:
        - seed_img/drug.png
        - seed_img/pharmacy_img.jpg
        - seed_img/profile.png
    """

    profile_img = "seed_img/profile.png"

    provinces = ["Mansour", "Kadhimiya", "Al Jamaa"]
    profile_users = []
    for user_ in range(12):
        
        user = User.objects.filter(email= f'user{user_}@example.com')
        if user.exists():
            user = user.first()
        else:
            user = User.objects.create_user(
                email= f'user{user_}@example.com',
                password= 'String1@',
            )

        profile, _ = Profile.objects.get_or_create(
            user=user, 
            name='BASBOS',
            img=profile_img,
            city="Baghdad",
            province=random.choice(provinces)
        )
        # create empty Cart for the user
        Cart.objects.create(user=profile)

        profile_users.append(profile)

    pharmacy_img = "seed_img/pharmacy_img.jpg"

    pharmacies = []
    names_1 = ['nahr','Kauthar','alsiha','life']
    names_2 = ['aldawaa','alyasameen','elixer','dalya']
    current_id = 0

    for i in range(10):
        pharmacy, _ = Pharmacy.objects.get_or_create(
                name=f"{i} {names_1[current_id]} {names_2[current_id]}",
                description="A family-owned pharmacy that has been serving the community",
                location=f"{random.choice(provinces)} / alroad / cross meshmesha",
                img=pharmacy_img,
        )
        current_id = current_id+1 if current_id < len(names_1)-1 else 0

        # create opening hours
        for choice in OpeningHours.DayChoices.choices:
            choice = choice[0]
            open_hours, created = OpeningHours.objects.get_or_create(weekday=choice,
                                                               pharmacy=pharmacy,)
            if created:
                hours = "9:00 AM - 9:00 PM"
                if choice == "FRI":
                    hours = "closed"

                open_hours.hours = hours
                open_hours.save()

        # create reviews
        for usr_indx in range(12):
            review = Review.objects.filter(user=profile_users[usr_indx],
                                         pharmacy=pharmacy,)
            if review.exists():
                continue

            Review.objects.create(user=profile_users[usr_indx],
                                         pharmacy=pharmacy,
                                         rating=random.uniform(0.0, 5.0),
                                         description=REVIEW_DESCRIPTION,)

        pharmacies.append(pharmacy)


    drug_img = "seed_img/drug.png"
    drug_names = ['Aspirin', 'Ibuprofen', 'Acetaminophen', 'Morphine', "Ibuprofen 200mg tablets"]

    for pharmacy_ in range(len(pharmacies)):
        for drug_ in range(20):
            Drug.objects.get_or_create(
                name = f"{drug_} {random.choice(drug_names)}",
                description ="Pain relief for headaches, toothaches, menstrual cramps, and other minor aches and pains.",
                img = drug_img,
                price=4.99,
                is_active=True,
                pharmacy=pharmacies[pharmacy_],
            )


    return status.HTTP_200_OK, SeedSchema(
        pharmacies= pharmacies,
        profile= profile_users[1]
        )


@draft_router.put("remove_from_cart/{drug_id}",
                  response={
                      200: ItemUpdate,
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

