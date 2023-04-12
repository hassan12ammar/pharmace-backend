from django.contrib import admin
from .models import Pharmacy, Drug, DrugItem, Cart


# reverse foreign key
class DrugItemAdmin(admin.TabularInline):
    model = DrugItem

class DrugAdmin(admin.TabularInline):
    model = Drug


class PharmacyAdmin(admin.ModelAdmin):
    model = Pharmacy
    inlines = [DrugAdmin]

class CartAdmin(admin.ModelAdmin):
    model = Cart
    inlines = [DrugItemAdmin]


# Register the models.
admin.site.register(Pharmacy, PharmacyAdmin)
admin.site.register(Cart, CartAdmin)

