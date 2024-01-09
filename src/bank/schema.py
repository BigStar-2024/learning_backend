import graphene
from graphene_django import DjangoObjectType
from bank.models import (
    BankWallet,
    Interest
)
from accounting.models import BankMovement

class BankWalletSchema(DjangoObjectType):
    class Meta:
        model = BankWallet
        fields = "__all__"


class BankMovementSchema(DjangoObjectType):
    class Meta:
        model = BankMovement
        # fields = ("amount","date")
        fields = "__all__"

    # transaction_type = graphene.String()

    # def resolve_transaction_type(self,info):
    #     if self.side == 'L':
    #         return "withdraw"
    #     elif self.side == 'R':
    #         return "deposit"
    #     return ""

class InterestSchema(DjangoObjectType):
    class Meta:
        model = Interest
        fields= "__all__"

class Query(graphene.ObjectType):
    # ----------------- Student Bank Balance ----------------- #

    student_bank_balance_by_id = graphene.Field(
        BankWalletSchema, student=graphene.ID())

    def resolve_student_bank_balance_by_id(root, info, student):
        # Querying a student's bank balance
        return BankWallet.objects.get(student=student)

    # ----------------- Student Bank Transactions ----------------- #

    student_bank_transactions_by_id = graphene.List(
        BankMovementSchema, student=graphene.ID())

    def resolve_student_bank_transactions_by_id(root, info, student):
        # Querying a student's transaction
        return BankMovement.objects.filter(account__student=student)

    # ----------------- Interest -------------------------------- #

    interests = graphene.List(
        InterestSchema
    )
    def resolve_interests(root, info, **kwargs):
        # Querying a list
        return Interest.objects.all()
