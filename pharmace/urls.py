""" pharmace URL Configuration """
from ninja import NinjaAPI
from django.urls import path
from django.contrib import admin
# local models
from pharmace.utlize.constant import DESCRIPTION
from core.controllers import pharmacy_router, cart_router, draft_router
from auth_profile.controllers import auth_controller, profile_controller

api = NinjaAPI(title="pharmace Backend", 
                description=DESCRIPTION)
api.add_router("auth", auth_controller, tags=["Auth"])
api.add_router("profile", profile_controller, tags=["Profile"])
# 
api.add_router("pharmacy", pharmacy_router, tags=["Pharmacy"])
api.add_router("cart", cart_router, tags=["Cart"])
api.add_router("draft", draft_router, tags=["Draft"])


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
