import graphene
from graphene_django import DjangoObjectType
from .models import WeeklyTreasure, WeeklyTreasureLevel, StudentWeeklyTreasure, WeeklyTreasureTransaction


class WeeklyTreasureSchema(DjangoObjectType):
    class Meta:
        model = WeeklyTreasure
        fields = "__all__"


class WeeklyTreasureLevelSchema(DjangoObjectType):
    class Meta:
        model = WeeklyTreasureLevel
        fields = "__all__"


class StudentWeeklyTreasureSchema(DjangoObjectType):
    class Meta:
        model = StudentWeeklyTreasure
        fields = "__all__"


class WeeklyTreasureTransactionSchema(DjangoObjectType):
    class Meta:
        model = WeeklyTreasureTransaction
        fields = "__all__"


class Query(graphene.ObjectType):

    # ----------------- WeeklyTreasure ----------------- #

    weekly_treasures = graphene.List(WeeklyTreasureSchema)
    weekly_treasure_by_id = graphene.Field(
        WeeklyTreasureSchema,
        id=graphene.ID()
    )

    def resolve_weekly_treasures(root, info, **kwargs):
        return WeeklyTreasure.objects.all()

    def resolve_weekly_treasure_by_id(root, info, id):
        return WeeklyTreasure.objects.get(id=id)

    # ----------------- WeeklyTreasureLevel ----------------- #

    weekly_treasure_levels = graphene.List(WeeklyTreasureLevelSchema)
    weekly_treasure_level_by_id = graphene.Field(
        WeeklyTreasureLevelSchema,
        id=graphene.ID()
    )

    def resolve_weekly_treasure_levels(root, info, **kwargs):
        return WeeklyTreasureLevel.objects.all()

    def resolve_weekly_treasure_level_by_id(root, info, id):
        return WeeklyTreasureLevel.objects.get(id=id)

    # ----------------- StudentWeeklyTreasure ----------------- #

    student_weekly_treasures = graphene.List(StudentWeeklyTreasureSchema)
    student_weekly_treasure_by_id = graphene.Field(
        StudentWeeklyTreasureSchema,
        id=graphene.ID()
    )

    def resolve_student_weekly_treasures(root, info, **kwargs):
        return StudentWeeklyTreasure.objects.all()

    def resolve_student_weekly_treasure_by_id(root, info, id):
        return StudentWeeklyTreasure.objects.get(id=id)

    # ----------------- WeeklyTreasureTransaction ----------------- #

    weekly_treasure_transactions = graphene.List(WeeklyTreasureTransactionSchema)
    weekly_treasure_transaction_by_id = graphene.Field(
        WeeklyTreasureTransactionSchema,
        id=graphene.ID()
    )

    def resolve_weekly_treasure_transactions(root, info, **kwargs):
        return WeeklyTreasureTransaction.objects.all()

    def resolve_weekly_treasure_transaction_by_id(root, info, id):
        return WeeklyTreasureTransaction.objects.get(id=id)
