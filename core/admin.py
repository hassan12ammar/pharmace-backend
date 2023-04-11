from django.contrib import admin
from .models import Pharmacy, Drug, DrugItem, Cart


# Register models.
admin.site.register(Pharmacy)
admin.site.register(Drug)
admin.site.register(DrugItem)
admin.site.register(Cart)

