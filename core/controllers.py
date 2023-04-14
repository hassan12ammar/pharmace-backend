from typing import List
from ninja import Router
from rest_framework import status
# locall models
from .models import Cart, DrugItem, Pharmacy, Review, Drug
from pharmace.utlize.custom_classes import Error
from auth_profile.authentication import CustomAuth
from pharmace.utlize.utlize import get_user_profile
from .schemas import (CartOut, DrugItemOut, PharmacyOut, 
                      PharmacyShort, MessageOut, ReviewOut)

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


