from typing import List
from ninja import Schema
from datetime import date, time
# local models
from auth_profile.schemas import ProfileOut
from core.models import Drug


# General Schemas
class MessageOut(Schema):
    detail: str


class ProfileReview(Schema):
    name: str
    img: str = None


class DrugSchema(Schema):
    name: str
    description: str
    img: str = None
    price: float


class DrugIn(DrugSchema):
    pass


class DrugOut(DrugSchema):
    id: int


class ReviewSchema(Schema):
    rating: float
    description: str = None


class ReviewIn(ReviewSchema):
    Pharmacy_id: int


class ReviewOut(ReviewSchema):
    start_date: date
    user: ProfileReview


class OpeningHoursSchema(Schema):
    weekday: str
    from_hour: time
    to_hour: time


class PharmacyShort(Schema):
    id: int
    name: str
    description: str
    img: str
    location: str

    avg_stars: float

    @staticmethod
    def resolve_avg_stars(self):
        reviews = self.review_set.all()
        rates = [review.rating 
                 for review in reviews]

        return sum(rates) / len(rates)    


class PharmacySchema(Schema):
    name: str
    description: str
    img: str
    location: str
    drugs: List[DrugOut]

    pct_rates: dict = None
    opening_hours: List[OpeningHoursSchema]

    @staticmethod
    def resolve_opening_hours(self):
        return self.opening_hours.all()

    @staticmethod
    def resolve_drugs(self):
        return Drug.objects.filter(pharmacy=self)

    @staticmethod
    def resolve_pct_rates(self):
        rates = [round(review.rating) 
                 for review in self.review_set.all()]

        if not rates:
            return

        counts = {i: rates.count(i) 
                  for i in range(1, 5 +1)}
        percentages = {i: round(counts[i] / len(rates) * 100) 
                       for i in range(1, 6)}

        return percentages


class PharmacyIn(PharmacySchema):
    pass


class PharmacyOut(PharmacySchema):
    id: int


""" Cart Schemas """


class DrugItemSchema(Schema):
    amount: int


class DrugItemIn(DrugItemSchema):
    drug_id: int


class DrugItemOut(DrugItemSchema):
    drug: DrugOut
    total: float

    @staticmethod
    def resolve_total(self):
        return self.drug.price * self.amount


class CartSchema(Schema):
    user: ProfileOut
    items: List[DrugItemOut]
    ordered: bool
    start_date: date
    ordered_date: date
    shipping: float

    total: float

    @staticmethod
    def resolve_total(self):
        return sum([
            item.total
            for item in self.items.all()
        ])


class CartIn(CartSchema):
    pass


class CartOut(CartSchema):
    pass
