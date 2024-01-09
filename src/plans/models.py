from django.db import models
from django.utils.text import slugify
from app.models import RandomSlugModel, TimestampModel, IsActiveModel
from organization.models.schools import Classroom, Teacher, TeacherClassroom
from payments.card import Card
from math import isclose

class Plan(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'plan_'

    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=False, blank=False, default = "")
    product_id = models.CharField(max_length=255, null=True, blank = True)
    area_of_knowledge = models.CharField(max_length=255, choices=(
        ("ALL", "ALL"), ("ONE", "ONE"), ("TWO", "TWO")), default="ALL", blank=True, null=True)
    slug = models.SlugField(editable=False)
    price_month = models.DecimalField(
        max_digits=15, decimal_places=3, default=0)
    price_preferential_month = models.DecimalField(
        max_digits=15, decimal_places=3, default=0)
    quantity_preferential_month = models.IntegerField(null=False, default = 2)
    price_year = models.DecimalField(
        max_digits=15, decimal_places=3, default=0)
    price_preferential_year = models.DecimalField(
        max_digits=15, decimal_places=3, default=0)
    quantity_preferential_year = models.IntegerField(null=False, default = 2)
    quantity_lower_limit = models.IntegerField(null=False, default = 1)
    currency = models.CharField(max_length=4)
    stripe_monthly_plan_id = models.CharField(max_length=255, blank=True)
    stripe_monthly_plan_preferential_price_id = models.CharField(
        max_length=255, blank=True)
    stripe_yearly_plan_id = models.CharField(max_length=255, blank=True)
    stripe_yearly_plan_preferential_price_id = models.CharField(
        max_length=255, blank=True)
    is_cancel = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        card = Card()
        self.slug = slugify(self.name)
        is_update = True if self.pk else False
        if is_update:
            price = {
                "price_month": 0,
                "price_preferential_month": 0,
                "quantity_preferential_month": 0,
                "price_year": 0,
                "price_preferential_year": 0,
                "quantity_preferential_year": 0,
            }
            #---------------- Get price object from stripe by id and get price and quantity from price obj -S-----------------#
            monthly_price = card.get_price_by_id(id = self.stripe_monthly_plan_id)
            print(monthly_price)
            try:

                for tier in monthly_price.tiers:
                    if(tier.up_to is not None):
                        price['price_month'] = float(tier.unit_amount_decimal) / 100
                        price['quantity_preferential_month'] = int(tier.up_to) + 1

                monthly_preferential_price = card.get_price_by_id(id = self.stripe_monthly_plan_preferential_price_id)
                for tier in monthly_preferential_price.tiers:
                    if(tier.up_to is None):
                        price['price_preferential_month'] = float(tier.unit_amount_decimal) / 100
                        

                yearly_price = card.get_price_by_id(id = self.stripe_yearly_plan_id)
                for tier in yearly_price.tiers:
                    if(tier.up_to is not None):
                        price['price_year'] = float(tier.unit_amount_decimal) / 100
                        price['quantity_preferential_year'] = int(tier.up_to) + 1

                yearly_preferential_price = card.get_price_by_id(id = self.stripe_yearly_plan_preferential_price_id)
                for tier in yearly_preferential_price.tiers:
                    if(tier.up_to is None):
                        price['price_preferential_year'] = float(tier.unit_amount_decimal) / 100
            except Exception as e:
                print(e)
            #---------------- Get price object from stripe by id and get price and quantity from price obj -E-----------------#

            #---------------- If price is not equal with price in strip, create another price in the strip -S-----------------#
            if( not(isclose(self.price_month, price['price_month'])) or
                not(isclose(self.price_preferential_month, price['price_preferential_month'])) or
                self.quantity_preferential_month != price['quantity_preferential_month'] or
                not(isclose(self.price_year, price['price_year'])) or
                not(isclose(self.price_preferential_year, price['price_preferential_year'])) or
                self.quantity_preferential_year != price['quantity_preferential_year']
            ):
                prices = card.create_price(
                    product_id =self.product_id,
                    price_month = self.price_month,
                    price_preferential_month = self.price_preferential_month,
                    quantity_preferential_month = self.quantity_preferential_month,
                    price_year = self.price_year,
                    price_preferential_year = self.price_preferential_year,
                    quantity_preferential_year = self.quantity_preferential_year
                )
                try:
                    card.delete_price(price_id = self.stripe_monthly_plan_id)
                    card.delete_price(price_id = self.stripe_monthly_plan_preferential_price_id)
                    card.delete_price(price_id = self.stripe_yearly_plan_id)
                    card.delete_price(price_id = self.stripe_yearly_plan_preferential_price_id)
                except Exception as e :
                    print(e)

                self.stripe_monthly_plan_id = prices['price_month'].id
                self.stripe_monthly_plan_preferential_price_id = prices['price_month'].id
                self.stripe_yearly_plan_id = prices['price_year'].id
                self.stripe_yearly_plan_preferential_price_id = prices['price_year'].id 
            #---------------- If price is not equal with price in strip, create another price in the strip -E-----------------#
             
        else:
            product = card.create_product(name = self.name, description = self.description)
            self.product_id = product.id
            prices = card.create_price(
                    product_id =self.product_id,
                    price_month = self.price_month,
                    price_preferential_month = self.price_preferential_month,
                    quantity_preferential_month = self.quantity_preferential_month,
                    price_year = self.price_year,
                    price_preferential_year = self.price_preferential_year,
                    quantity_preferential_year = self.quantity_preferential_year
                )

            self.stripe_monthly_plan_id = prices['price_month'].id
            self.stripe_monthly_plan_preferential_price_id = prices['price_month'].id
            self.stripe_yearly_plan_id = prices['price_year'].id
            self.stripe_yearly_plan_preferential_price_id = prices['price_year'].id 
        return super().save(*args, **kwargs)


class GuardianStudentPlan(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'guardian_student_plan_'

    guardian = models.ForeignKey(
        'guardians.Guardian', on_delete=models.PROTECT)
    student = models.OneToOneField(
        'students.Student', on_delete=models.PROTECT, blank=True, null=True)
    order_detail = models.ForeignKey(
        'payments.OrderDetail', on_delete=models.CASCADE)
    slug = models.SlugField(editable=False)
    plan = models.ForeignKey('Plan', on_delete=models.PROTECT, blank=True)
    subject = models.ManyToManyField(
        'kb.AreaOfKnowledge',
        blank=True
    )
    cancel_reason = models.TextField(blank=True)
    is_cancel = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    expired_at = models.DateTimeField(null=True)
    period = models.CharField(
        max_length=100,
        choices=(("MONTHLY", "Monthly"), ("YEARLY", "Yearly")),
        default="MONTHLY"
    )
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return str(self.id)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        return super().save(*args, **kwargs)


class StudentPlan(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'student_plan_'

    name = models.CharField(max_length=128)
    slug = models.SlugField(editable=False)
    audience = models.ForeignKey(
        'audiences.Audience',
        on_delete=models.PROTECT,
    )
    topic_grade = models.ManyToManyField(
        'kb.TopicGrade',
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
