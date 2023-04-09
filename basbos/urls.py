""" basbos URL Configuration """
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
# local models
from auth_profile.controllers import auth_controller, profile_controller


api = NinjaAPI(title="BASBOS Backend", 
                description="Backend of E-commerc for pharmacies website using Django and Ninja")
api.add_router("auth", auth_controller, tags=["Auth"])
api.add_router("auth", profile_controller, tags=["Profile"])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
