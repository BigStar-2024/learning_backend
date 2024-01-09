import graphene
from django.utils import timezone

from students.schema import StudentSchema
from .models import WeeklyTreasure, StudentWeeklyTreasure, WeeklyTreasureTransaction, WeeklyTreasureLevel
from students.models import Student
from datetime import timedelta
from block.models import BlockTransaction, BlockQuestionPresentation
from django.db.models.functions import TruncDay
from django.db.models import Sum, Count
from django.db.models import Max
from .cron import giveWeeklyBonus
class RedeemWeeklyTreasure(graphene.Mutation):
    student_weekly_treasure = graphene.Field(
        'treasuretrack.schema.StudentWeeklyTreasureSchema'
    )
    weekly_treasure_transaction = graphene.Field(
        'treasuretrack.schema.WeeklyTreasureTransactionSchema'
    )

    class Arguments:
        student_id = graphene.ID()
        weekly_treasure_id = graphene.ID(required=True)

    def mutate(self, info, weekly_treasure_id, student_id=None):
        if student_id is None:
            user = info.context.user

            if not user.is_authenticated:
                raise Exception("Authentication credentials were not provided")
            if not user.student:
                raise Exception("Not found student")

            student = user.student
        else:
            student = Student.objects.get(id=student_id)

        weekly_treasure = WeeklyTreasure.objects.get(id=weekly_treasure_id)

        student_weekly_treasure, new = StudentWeeklyTreasure.objects.get_or_create(
            student=student,
            weekly_treasure=weekly_treasure,
            create_timestamp=timezone.now().date()
        )

        if new:
            weekly_treasure_transaction = WeeklyTreasureTransaction(
                weekly_treasure=weekly_treasure,
                account=student.coinWallet
            )

        return RedeemWeeklyTreasure(
            student_weekly_treasure=student_weekly_treasure,
            weekly_treasure_transaction=weekly_treasure_transaction
        )

class GiveWeeklyBonus(graphene.Mutation):
    students = graphene.List(StudentSchema)

    def mutate(self, info):
        students = Student.objects.all()
        giveWeeklyBonus()
        return GiveWeeklyBonus(
            students = students
        )
        
class Mutation(graphene.ObjectType):
    redeem_weekly_treasure = RedeemWeeklyTreasure.Field()
    GiveWeeklyBonus = GiveWeeklyBonus.Field()

