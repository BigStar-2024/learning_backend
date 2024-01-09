import graphene
from graphene_django import DjangoObjectType
from guardians.models import Guardian, GuardianStudent
from payments.models import PaymentMethod, DiscountCode
from plans.models import GuardianStudentPlan
from plans.schema import GuardianStudentPlanSchema


class GuardianSchema(DjangoObjectType):

    class Meta:
        model = Guardian
        fields = "__all__"

    coupon_code = graphene.Field('payments.schema.DiscountCodeSchema')
    payment_method = graphene.Field('payments.schema.PaymentMethodSchema')
    available_guardianstudentplan = graphene.List(GuardianStudentPlanSchema)
    def resolve_payment_method(self, info):
        payment_method = PaymentMethod.objects.filter(is_default=True, guardian_id=self.id)
        if payment_method.count() != 0:
            return payment_method[0]
        return

    def resolve_coupon_code(self, info):
        if self.coupon_code:
            discount = DiscountCode.objects.get(pk=self.coupon_code.id)
            return discount
        return None

    def resolve_available_guardianstudentplan(self, inof):
        available = GuardianStudentPlan.objects.filter(guardian = self, student = None)
        return available



class GuardianStudentSchema(DjangoObjectType):
    class Meta:
        model = GuardianStudent
        fields = "__all__"


class Query(graphene.ObjectType):
    # ----------------- Guardian ----------------- #

    guardians = graphene.List(GuardianSchema)
    guardian_by_id = graphene.Field(GuardianSchema, id=graphene.String())

    def resolve_guardians(root, info, **kwargs):
        # Querying a list
        return Guardian.objects.all()

    def resolve_guardian_by_id(root, info, id):
        # Querying a single question
        return Guardian.objects.get(pk=id)

    # ----------------- GuardianStudent ----------------- #

    guardians_student = graphene.List(GuardianStudentSchema)
    guardian_student_by_id = graphene.Field(
        GuardianStudentSchema, id=graphene.String())
    guardian_student_by_guardian_id = graphene.List(
        GuardianStudentSchema, id=graphene.ID())

    def resolve_guardians_student(root, info, **kwargs):
        # Querying a list
        return GuardianStudent.objects.all()

    def resolve_guardian_student_by_id(root, info, id):
        # Querying a single question
        return GuardianStudent.objects.get(pk=id)

    def resolve_guardian_student_by_guardian_id(root, info, id):
        # Querying a single question
        return GuardianStudent.objects.filter(guardian=id)
