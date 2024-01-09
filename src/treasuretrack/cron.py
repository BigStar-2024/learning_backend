from badges.models import StudentBadge
from .models import WeeklyTreasure, StudentWeeklyTreasure, WeeklyTreasureTransaction, WeeklyTreasureLevel
from students.models import Student
from block.models import BlockQuestionPresentation

from django.utils import timezone
from django.db.models.functions import TruncDay
from django.db.models import Count
from datetime import timedelta

def giveWeeklyBonus():
    students = Student.objects.all()
    print("===========Starting Give Weekly Bonus/"+timezone.now().strftime("%Y/%m/%d, %H:%M:%S")+"=============" )
    for student in students:
        today = timezone.now()
        most_recent_monday = today - timedelta(days=(today.isoweekday()-1))
        start_date = most_recent_monday - timedelta(days=7*(1-1))
        last_week_questions_data = (BlockQuestionPresentation.objects
            .filter(
                block_presentation__block__students=student
            )
            .filter(status="CORRECT")
            .filter(create_timestamp__range=(start_date, today))
            .annotate(day=TruncDay("create_timestamp"))
            .values("day")
            .annotate(questions=Count("id"))
            .values("day", "questions")
            .order_by("day")
        )
        correct_questions_count = 0
        
        for last_weekquestion_data in last_week_questions_data:
            correct_questions_count += last_weekquestion_data['questions']

        if(correct_questions_count < 1): continue

        available_levels = (WeeklyTreasureLevel.objects
            .filter(correct_questions_required__lte=correct_questions_count)
            .order_by('correct_questions_required')
            # .annotate(max_correct_questions_required=Max('correct_questions_required'))
            # .values('bonus_coins', 'bonus_collectible')
            # .query
            )
        if(len(available_levels.all()) < 1): continue

        if((StudentWeeklyTreasure.objects
                .filter(student = student)
                .filter(create_timestamp__range=(start_date, today))
                .annotate(day=TruncDay("create_timestamp"))
                .values("day")
                .annotate(questions=Count("id"))
                .values("day", "questions")
                .order_by("day")
        )):
            # print("fixed")
            continue
        # print("will do")
        current_level = available_levels.all()[0]
        bonus_coins = current_level.bonus_coins
        bonus_collectibles = current_level.bonus_collectible

        weekly_tresure = WeeklyTreasure(level=current_level)
        weekly_tresure.collectibles_awarded_set = bonus_collectibles
        print(current_level.id)
        print(current_level.bonus_badge)
        weekly_tresure.badge_awarded = current_level.bonus_badge
        weekly_tresure.coins_awarded = bonus_coins
        weekly_tresure.save()
        print("Weekly Treasure ID : ", weekly_tresure.id, " Saved !")
        if(current_level.bonus_badge) :
            StudentBadge.objects.create(badge = current_level.bonus_badge, student=student, weekly_tresure=weekly_tresure)
        student_weekly_treasure = StudentWeeklyTreasure(student=student, weekly_treasure=weekly_tresure)
        student_weekly_treasure.save()

        weeklyTreasureTransaction = WeeklyTreasureTransaction(student_weekly_treasure=student_weekly_treasure,account=student.coinWallet)
        weeklyTreasureTransaction.save()

    print("===========Finishing Give Weekly Bonus/"+timezone.now().strftime("%Y/%m/%d, %H:%M:%S")+"=============" )

