""" pharmace URL Configuration """
from ninja import NinjaAPI
from django.urls import path
from django.contrib import admin
# local models
from core.controllers import pharmacy_router, cart_router
from auth_profile.controllers import auth_controller, profile_controller


api = NinjaAPI(title="pharmace Backend", 
                description="Backend of E-commerc for pharmacies website using Django and Ninja")
api.add_router("auth", auth_controller, tags=["Auth"])
api.add_router("profile", profile_controller, tags=["Profile"])
# 
api.add_router("pharmacy", pharmacy_router, tags=["Pharmacy"])
api.add_router("cart", cart_router, tags=["Cart"])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
