from typing import List
from ninja import Router
from rest_framework import status
# locall models
from .models import Cart, DrugItem, Pharmacy, Review, Drug
from pharmace.utlize.custom_classes import Error
from auth_profile.authentication import CustomAuth
from pharmace.utlize.utlize import get_user_profile
from .schemas import (CartOut, DrugItemOut, PharmacyOut, 
                      PharmacyShort, MessageOut, ReviewIn, ReviewOut)

# 
pharmacy_router = Router()
cart_router = Router()


""" Pharmacy """
@pharmacy_router.get("get_all",
                     response={
                         200:List[PharmacyShort],
                     })
def get_all(request):
    return status.HTTP_200_OK, Pharmacy.objects.all()


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
    email = request.auth

    # get user profile
    profile = get_user_profile(email)
    if isinstance(profile, Error):
        return profile.status, profile.message

    pharmacy = Pharmacy.objects.filter(name__contains=name).filter(location__contains=profile.state)

    return status.HTTP_200_OK, pharmacy


@pharmacy_router.post("add_edit_review",
                      response={200: ReviewOut,
                                400: MessageOut,
                                404: MessageOut},
                      auth=CustomAuth(),)
def add_edit_review(request, review_in: ReviewIn):
    # get the user from email in auth
    email = request.auth

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
    email = request.auth

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
    email = request.auth

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
    email = request.auth

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


@cart_router.put("remove_from_cart/{drug_id}",
                  response={
                      200: DrugItemOut,
                      400: MessageOut,
                      404: MessageOut,
                  },
                auth=CustomAuth(),)
def remove_from_cart(request, drug_id: int):
    # get the user from email in auth
    email = request.auth

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



@cart_router.put("decrease_from_cart/{drug_id}",
                  response={
                      200: DrugItemOut,
                      400: MessageOut,
                      404: MessageOut,
                  },
                auth=CustomAuth(),)
def decrease_from_cart(request, drug_id: int):
    # get the user from email in auth
    email = request.auth

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


