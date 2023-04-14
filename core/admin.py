from django.contrib import admin
from .models import OpeningHours, Pharmacy, Drug, DrugItem, Cart, Review


# reverse foreign key
class DrugItemAdmin(admin.TabularInline):
    model = DrugItem

class DrugAdmin(admin.TabularInline):
    model = Drug

class ReviewAdmin(admin.TabularInline):
    model = Review

class OpeningHoursAdmin(admin.TabularInline):
    model = OpeningHours


class PharmacyAdmin(admin.ModelAdmin):
    model = Pharmacy
    inlines = [DrugAdmin, ReviewAdmin, OpeningHoursAdmin]

class CartAdmin(admin.ModelAdmin):
    model = Cart
    inlines = [DrugItemAdmin]


# Register the models.
admin.site.register(Pharmacy, PharmacyAdmin)
admin.site.register(Cart, CartAdmin)

