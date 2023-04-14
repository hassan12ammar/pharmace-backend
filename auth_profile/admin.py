from django.contrib import admin
from core.models import Cart
# locall models
from pharmace.forms import CustomUserForm
from .models import CustomUser, Profile


class CustomUserAdmin(admin.ModelAdmin):
    # using custom form to validate password
    form = CustomUserForm
    # override default save method to hash password 
    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        obj.set_password(obj.password)
        obj.save()


class CartAdminInline(admin.TabularInline):
    model = Cart
    

class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    inlines = [CartAdminInline]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
