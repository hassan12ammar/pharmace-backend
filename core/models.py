from django.db import models
# from typing import Optional

class Review(models.Model):
    """
    user
    rating stars
    description (pptional)
    """
    pass

class Pharmacy(models.Model):
    """
    name
    description
    drugs
    img
    location
    reviews
    """
    pass

class Drug(models.Model):
    """
    name
    desription
    price
    """
    pass

class DrugItem(models.Model):
    """
    drugs
    amount
    total (property)
    """
    pass

class Cart(models.Model):
    """
    user
    items
    date (start & ordered )
    ordered (bool)
    """
    pass


