from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Review(models.Model):
    user = models.OneToOneField("auth_profile.Profile", 
                                verbose_name=("user_profile"), 
                                on_delete=models.CASCADE)
    rating = models.FloatField("rate stars", 
                               validators=[
                                   MinValueValidator(0),
                                   MaxValueValidator(5),
                               ])
    description = models.CharField(max_length=500, null=True)
    pharmacy = models.ForeignKey("core.Pharmacy", on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} / {self.rating}"


class OpeningHours(models.Model):
    class DayChoices(models.TextChoices):
        SAN = "SAN"
        MON = "MON"
        TUE = "TUE"
        WED = "WED"
        THU = "THU"
        FRI = "FRI"
        SAT = "SAT"

    weekday = models.CharField(max_length=3, choices=DayChoices.choices)
    from_hour = models.TimeField()
    to_hour = models.TimeField()

    pharmacy = models.ForeignKey("core.Pharmacy", 
                                 on_delete=models.CASCADE, 
                                 related_name='opening_hours')

    class Meta:
        unique_together = ['pharmacy', 'weekday']

    def __str__(self):
        return u'%s: %s - %s' % (self.get_weekday_display(),
                                 self.from_hour, self.to_hour)

class Pharmacy(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=750)

    img = models.ImageField(upload_to='pharmacy_imgs', null=True)
    location = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Drug(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=750)
    img = models.ImageField(upload_to='drug_imgs', 
                            null=True, blank=True)
    price = models.FloatField()
    is_active = models.BooleanField('is active')

    pharmacy = models.ForeignKey("core.Pharmacy", 
                              on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class DrugItem(models.Model):
    """
    Drug can live alone in the system, while
    Item can only live within the cart.
    """
    drug = models.ForeignKey("core.Drug", 
                             on_delete=models.CASCADE)
    amount = models.IntegerField()
    cart = models.ForeignKey("core.Cart", 
                             related_name="item_cart",
                             on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.drug} / {self.amount}"


class Cart(models.Model):
    class StatusChoices(models.TextChoices):
        # cart is empty or items in the basket.
        NEW = 'NEW'  
        # payment confirmed processing order.
        PROCESSING = 'PROCESSING'
        # Shipped to customer.
        SHIPPED = 'SHIPPED'
        # Completed and received by customer.
        COMPLETED = 'COMPLETED'

    user = models.OneToOneField("auth_profile.Profile", 
                                verbose_name=("user_profile"), 
                                on_delete=models.CASCADE)

    ordered = models.BooleanField("is ordered", default=False)
    status = models.CharField(max_length=15, choices=StatusChoices.choices)

    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.__str__()} cart"

