from typing import List, Optional
from ninja import Schema
from datetime import date
from django.db.models import Count, Q, Avg
from django.db.models.functions import Round
# local models
from core.models import Drug, Review
from auth_profile.schemas import ProfileOut
from pharmace.utlize.constant import DRUG_PER_PAGE, REVIEW_PER_PAGE


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
    
    @staticmethod
    def resolve_rating(self):
        return round(self.rating, 1)


class ReviewIn(ReviewSchema):
    Pharmacy_id: int


class ReviewOut(ReviewSchema):
    start_date: date
    user: ProfileReview


class OpeningHoursSchema(Schema):
    weekday: str
    hours: str


class PharmacyShort(Schema):
    id: int
    name: str
    description: str
    img: str
    location: str

    avg_stars: float
    pct_rates: dict = None

    @staticmethod
    def resolve_avg_stars(self):
        avg_rating = self.review_set.aggregate(avg_rating=Avg('rating'))['avg_rating']
        if avg_rating is None:
            return 0

        return round(avg_rating, 1)

    @staticmethod
    def resolve_pct_rates(self):

        has_reviews = self.review_set.exists()

        if not has_reviews:
            return

        rating_counts = self.review_set.filter(
            Q(rating__gte=0.5, rating__lt=1.5) |
            Q(rating__gte=1.5, rating__lt=2.5) |
            Q(rating__gte=2.5, rating__lt=3.5) |
            Q(rating__gte=3.5, rating__lt=4.5) |
            Q(rating__gte=4.5)
        ).annotate(rounded_rating=Round('rating')).values('rounded_rating').annotate(count=Count('id'))

        counts = {rating_count['rounded_rating']: rating_count['count'] for rating_count in rating_counts}
        total_count = sum(counts.values())
        percentages = {i: round(counts.get(i, 0) / total_count * 100)
                       for i in range(1, 6)}

        return percentages


class PharmacySchema(PharmacyShort):
    drugs: List[DrugOut]

    opening_hours: List[OpeningHoursSchema]

    @staticmethod
    def resolve_opening_hours(self):
        return self.opening_hours.all()

    @staticmethod
    def resolve_drugs(self):
        drugs = Drug.objects.filter(pharmacy=self)[:DRUG_PER_PAGE]

        return drugs


class PharmacyIn(PharmacySchema):
    pass


class PharmacyOut(PharmacySchema):
    id: int
    reviews: List[ReviewOut] = None

    @staticmethod
    def resolve_reviews(self):
        return Review.objects.filter(pharmacy=self).order_by("-id")[:REVIEW_PER_PAGE]


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
    shipping: Optional[float]

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


class SeedSchema(Schema):
    pharmacies: List[PharmacyOut]
    profile: ProfileOut