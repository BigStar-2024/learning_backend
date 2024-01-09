from django.db import models
from django.utils.text import slugify
from app.models import RandomSlugModel, TimestampModel, IsActiveModel
from app.models import RandomSlugModel, TimestampModel, IsActiveModel, ActiveManager
from users.models import User


PAYMENT_METHOD = (("CARD", "CARD"), ("PAYPAL", "PAYPAL"), ("APPLEPAY", "APPLEPAY"), ("FREE", "FREE"))


class Order(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'order_'

    guardian = models.ForeignKey('guardians.Guardian', on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey('organization.Teacher', on_delete=models.CASCADE, null=True)
    school = models.ForeignKey('organization.School', on_delete=models.CASCADE, null=True)
    sub_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_code = models.CharField(max_length=255, blank=True)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=255, choices=PAYMENT_METHOD, default="CARD")
    is_paid = models.BooleanField(default=False)
    slug = models.SlugField(editable=False)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        return super().save(*args, **kwargs)


class OrderDetail(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'order_detail_'

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    plan = models.ForeignKey('plans.Plan', on_delete=models.CASCADE)
    payment_method_plan_id = models.CharField(max_length=255)
    subscription_id = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    period = models.CharField(
        max_length=100,
        choices=(("MONTHLY", "Monthly"), ("YEARLY", "Yearly")),
        default="MONTHLY"
    )
    update_from_detail_id = models.IntegerField(default=0)
    status = models.CharField(max_length=255, blank=True, null=True)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    on_discount = models.BooleanField(default=False)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    expired_at = models.DateTimeField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    cancel_reason = models.TextField(blank=True)
    is_cancel = models.BooleanField(default=False)
    slug = models.SlugField(editable=False)
    error_message = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        return super().save(*args, **kwargs)


class PaypalTransaction(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'paypal_transaction_'

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    token_id = models.CharField(max_length=255)
    approve_link = models.TextField()
    capture_link = models.TextField()
    is_captured = models.BooleanField(default=False)
    slug = models.SlugField(editable=False)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        return super().save(*args, **kwargs)


class CardTransaction(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'card_transaction_'

    order_detail = models.ForeignKey(OrderDetail, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255)
    approve_link = models.TextField()
    card_first_name = models.CharField(max_length=255, blank=True, null=True)
    card_last_name = models.CharField(max_length=255, blank=True, null=True)
    card_number = models.CharField(max_length=255, blank=True, null=True)
    card_exp_month = models.CharField(max_length=255, blank=True, null=True)
    card_exp_year = models.CharField(max_length=255, blank=True, null=True)
    card_cvc = models.CharField(max_length=255, blank=True, null=True)
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    post_code = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    is_captured = models.BooleanField(default=False)
    slug = models.SlugField(editable=False)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        return super().save(*args, **kwargs)

class PaymentMethodManager(ActiveManager):
    pass

class PaymentMethod(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'payment_method_'

    guardian = models.ForeignKey('guardians.Guardian', on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey('organization.Teacher', on_delete=models.CASCADE, null=True)
    school = models.ForeignKey('organization.School', on_delete=models.CASCADE, null=True)
    method = models.CharField(max_length=255, choices=PAYMENT_METHOD, default="CARD")
    card_first_name = models.CharField(max_length=255, blank=True, null=True)
    card_last_name = models.CharField(max_length=255, blank=True, null=True)
    card_number = models.CharField(max_length=255, blank=True, null=True)
    card_exp_month = models.CharField(max_length=255, blank=True, null=True)
    card_exp_year = models.CharField(max_length=255, blank=True, null=True)
    card_cvc = models.CharField(max_length=255, blank=True, null=True)
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    post_code = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    slug = models.SlugField(editable=False)
    
    objects = PaymentMethodManager()

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        return super().save(*args, **kwargs)


class DiscountCode(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'discount_code_'
    COUPON_FOREVER = 'FOREVER'
    COUPON_ONE_MONTH = 'ONE_MONTH'
    COUPON_TWO_MONTH = 'TWO_MONTH'
    COUPON_SIX_MONTH = 'SIX_MONTH'
    COUPON_ONE_YEAR = 'ONE_YEAR'

    COUPON_TYPE_CHOICES = (
        (COUPON_FOREVER, 'FOREVER'),
        (COUPON_ONE_MONTH, 'ONE_MONTH'),
        (COUPON_TWO_MONTH, 'TWO_MONTH'),
        (COUPON_SIX_MONTH, 'SIX_MONTH'),
        (COUPON_ONE_YEAR, 'ONE_YEAR'),

    )
    COUPON_FOR_GUARDIAN = 'FOR_GUARDIAN'
    COUPON_FOR_TEACHER = 'FOR_TEACHER'
    COUPON_FOR_SUBSCRIBER = 'FOR_SUBSCRIBER'
    COUPON_FOR_ALL = 'FOR_ALL'

    COUPON_FOR_CHOICES = (
        (COUPON_FOR_GUARDIAN, 'FOR_GUARDIAN'),
        (COUPON_FOR_TEACHER, 'FOR_TEACHER'),
        (COUPON_FOR_SUBSCRIBER, 'FOR_SUBSCRIBER'),
        (COUPON_FOR_ALL, 'FOR_ALL'),
    )

    code = models.CharField(max_length=255, unique=True)
    percentage = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    trial_day = models.IntegerField(default=0)
    expired_at = models.DateTimeField()
    stripe_coupon_id = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, choices=COUPON_TYPE_CHOICES, default = COUPON_ONE_MONTH)
    for_who = models.CharField(max_length=255, choices=COUPON_FOR_CHOICES, default = COUPON_FOR_ALL)
    slug = models.SlugField(editable=False)

    def __str__(self):
        return str(self.code)
        # return str(self.id)

    def save(self, *args, **kwargs):
        from payments.card import Card
        card = Card()

        self.slug = slugify(self.id)
        if self.percentage != 0 :
            if self.stripe_coupon_id is None:
                duration = "once"
                duration_in_months = None
                if self.type == self.COUPON_FOREVER:
                    duration = "forever"
                    duration_in_months = None
                elif self.type == self.COUPON_ONE_MONTH:
                    duration = "once"
                    duration_in_months = None
                elif self.type == self.COUPON_TWO_MONTH:
                    duration = "repeating"
                    duration_in_months = 2
                elif self.type == self.COUPON_SIX_MONTH:
                    duration = "repeating"
                    duration_in_months = 2
                elif self.type == self.COUPON_ONE_YEAR:
                    duration = "repeating"
                    duration_in_months = 12
                coupon = card.create_coupon(code = self.code, percentage = self.percentage, duration = duration, duration_in_months = duration_in_months)
                self.stripe_coupon_id = coupon.id
            else:
                coupon = card.get_coupon(id = self.stripe_coupon_id)
                if(coupon.name != self.code):
                    card.update_coupon(id = self.stripe_coupon_id, new_name = self.code)
        return super().save(*args, **kwargs)

class PaymentHistory(TimestampModel, RandomSlugModel):
    PREFIX = 'payment_history_'
    PAYMENT_EVENT_TYPE = (
        ("payment_action_intent_succeeded", "payment_action_intent_succeeded"),
        ("payment_action_intent_failed", "payment_action_intent_failed"),
        ("payment_action_customer_create", "payment_action_customer_create"),
        ("payment_action_customer_create_error", "payment_action_customer_create_error"),
        ("payment_action_customer_delete", "payment_action_customer_delete"),
        ("payment_action_customer_delete_error", "payment_action_customer_delete_error"),
        ("payment_action_subscription_create", "payment_action_subscription_create"),
        ("payment_action_subscription_create_error", "payment_action_subscription_create_error"),
        ("payment_action_subscription_cancel", "payment_action_subscription_cancel"),
        ("payment_action_coupon_create", "payment_action_coupon_create"),
        ("payment_action_coupon_create_error", "payment_action_coupon_create_error"),
        ("payment_action_subscription_cancel_error", "payment_action_subscription_cancel_error"),
        ("payment_action_payment_method_create", "payment_action_payment_method_create"),
        ("payment_action_payment_method_create_error", "payment_action_payment_method_create_error"),
        ("payment_action_payment_method_update", "payment_action_payment_method_update"),
        ("payment_action_payment_method_attach", "payment_action_payment_method_attach"),
        ("payment_action_payment_method_attach_error", "payment_action_payment_method_attach_error"),
        ("payment_action_payment_method_modify", "payment_action_payment_method_modify"),
        ("payment_action_payment_method_modify_error", "payment_action_payment_method_modify_error"),
        ("payment_action_webhook_construct_error", "payment_action_webhook_construct_error"),
        ("backend_anction_order_create", "backend_anction_order_create"),
        ("backend_anction_order_create_error", "backend_anction_order_create_error"),
        ("backend_anction_confirm_payment_order", "backend_anction_confirm_payment_order"),
        ("backend_anction_confirm_payment_order_error", "backend_anction_confirm_payment_order_error"),
        ("backend_anction_change_default_payment_method", "backend_anction_change_default_payment_method"),
        ("backend_anction_edit_payment_method", "backend_anction_edit_payment_method"),
        ("backend_anction_edit_payment_method_error", "backend_anction_edit_payment_method_error"),
        ("backend_anction_create_order_without_pay", "backend_anction_create_order_without_pay"),
        ("backend_anction_create_order_without_pay_error", "backend_anction_create_order_without_pay_error"),
    )
    type = models.CharField(max_length=255, choices=PAYMENT_EVENT_TYPE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255, null=True, blank=True)
    card_number = models.CharField(max_length=255, null=True, blank=True)
    amount = models.IntegerField(blank=True, null=True)
    @property
    def card_number_encrypted(self):
        str = None
        if(self.card_number):
            card_leng = len(self.card_number)
            first_4 = self.card_number[0:4]
            last_4 = self.card_number[card_leng-4:card_leng]
            str = f"{first_4} *** {last_4}"
        return str

    def save(self, *args, **kwargs):
        if self.message : self.message = self.message[:254]
        if not self.card_number and self.user:
            payment_method = PaymentMethod.objects.filter(is_default=True, guardian__user_id=self.user.id)
            if payment_method.count() != 0:
                self.card_number = payment_method[0].card_number
        return super().save(*args, **kwargs)


