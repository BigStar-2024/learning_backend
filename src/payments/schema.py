import graphene
from graphene_django import DjangoObjectType
from .models import Order, OrderDetail, PaymentMethod, DiscountCode


class DiscountCodeSchema(DjangoObjectType):
    class Meta:
        model = DiscountCode
        fields = "__all__"


class PaymentMethodSchema(DjangoObjectType):
    class Meta:
        model = PaymentMethod
        fields = "__all__"

    card_number = graphene.String()
    
    def resolve_card_number(self, info, language_code=None):
        str = None
        if(self.card_number):
            card_leng = len(self.card_number)
            first_4 = self.card_number[0:4]
            last_4 = self.card_number[card_leng-4:card_leng]
            str = f"{first_4} *** {last_4}"
        return str

class OrderDetailSchema(DjangoObjectType):
    class Meta:
        model = OrderDetail
        fields = "__all__"


class OrderSchema(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

        order_detail = graphene.List(OrderDetailSchema)

        def resolve_order_detail(self, info):
            order_detail_list = OrderDetail.objects.filter(order_id=self.id)
            return order_detail_list


class Query(graphene.ObjectType):
    # ----------------- Order ----------------- #
    orders = graphene.List(OrderSchema)
    order_by_id = graphene.Field(OrderSchema, id=graphene.String())

    def resolve_orders(self, info, **kwargs):
        # Querying a list
        return Order.objects.all()

    def resolve_order_by_id(self, info, id):
        # Querying a single question
        return Order.objects.get(pk=id)

    # ----------------- Order Detail ----------------- #
    order_details = graphene.List(OrderDetailSchema)
    order_detail_by_id = graphene.Field(OrderDetailSchema, id=graphene.String())
    order_detail_by_guardian_id = graphene.List(OrderDetailSchema, guardian_id=graphene.String())
    guardian_available_brought_plan = graphene.List(OrderDetailSchema, guardian_id=graphene.String())

    def resolve_order_details(self, info, **kwargs):
        # Querying a list
        return OrderDetail.objects.all()

    def resolve_order_detail_by_id(self, info, id):
        # Querying a single question
        return OrderDetail.objects.get(pk=id)

    def resolve_order_detail_by_guardian_id(self, info, guardian_id):
        return OrderDetail.objects.filter(order__guardian_id=guardian_id)

    def resolve_guardian_available_brought_plan(self, info, guardian_id):
        return OrderDetail.objects.filter(order__guardian_id=guardian_id, is_cancel=False)

    # ----------------- Payment Method ----------------- #
    payment_methods = graphene.List(PaymentMethodSchema)
    payment_method_id = graphene.Field(PaymentMethodSchema, id=graphene.String())

    def resolve_payment_methods(self, info, **kwargs):
        # Querying a list
        return PaymentMethod.objects.all()

    def resolve_payment_method_id(self, info, id):
        # Querying a single question
        return PaymentMethod.objects.get(pk=id)
