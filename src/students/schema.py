import graphene
from django.db.models import Sum, Count, F, Case, When, DecimalField, Q
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import date, timedelta
from graphene_django import DjangoObjectType
from block.schema import BlockSchema
from students.models import Student, StudentHomework, StudentTopicMastery, StudentGrade, StudentAchievement
from wallets.schema import CoinWalletSchema
from experiences.schema import LevelSchema
from guardians.models import GuardianStudent
from avatars.models import StudentAvatar
from block.models import Block, BlockPresentation, BlockTransaction, BlockQuestionPresentation, StudentBlockQuestionPresentationHistory
from treasuretrack.models import WeeklyTreasureLevel
from treasuretrack.schema import WeeklyTreasureLevelSchema


class CoinGraphType(graphene.ObjectType):
    day = graphene.Date()
    coins = graphene.Decimal()

    def resolve_day(self, info):
        return self['day']

    def resolve_coins(self, info):
        return self['coins']


class StudentHomeworkResultType(graphene.ObjectType):
    hits = graphene.Int()
    total = graphene.Int()

class StudentQuestionAnswerResultType(graphene.ObjectType):
    hits = graphene.Int()
    total = graphene.Int()


class QuestionsGraphType(graphene.ObjectType):
    day = graphene.Date()
    questions = graphene.Int()

    def resolve_day(self, info):
        return self['day']

    def resolve_questions(self, info):
        return self['questions']


class StudentSchema(DjangoObjectType):
    class Meta:
        model = Student
        fields = "__all__"

    coin_wallet = graphene.Field(CoinWalletSchema)
    grade = graphene.Field('students.schema.StudentGradeSchema')
    next_level = graphene.Field(LevelSchema)
    current_avatar_head = graphene.Field('avatars.schema.AvatarSchema')
    current_avatar_accessories = graphene.Field('avatars.schema.AvatarSchema')
    current_avatar_clothes = graphene.Field('avatars.schema.AvatarSchema')
    current_avatar_pants = graphene.Field('avatars.schema.AvatarSchema')
    user = graphene.Field('users.schema.UserSchema')
    last_week_coins = graphene.List(CoinGraphType, week_count=graphene.Int())
    last_week_questions = graphene.List(
        QuestionsGraphType,
        week_count=graphene.Int()
    )
    current_weekly_treasure_level = graphene.Field(WeeklyTreasureLevelSchema)
    total_questions_and_hits = graphene.Field(StudentQuestionAnswerResultType)
    today_coins = graphene.Int()
    thisweek_correct_questions = graphene.Int()

    def resolve_coin_wallet(self, info):
        return self.coinWallet

    def resolve_grade(self, info):
        student_grade = StudentGrade.objects.filter(
            student_id=self.id, is_active=True).order_by("-create_timestamp")
        if student_grade.count() != 0:
            return student_grade[0]
        return

    def resolve_next_level(self, info):
        # Get next level
        next_level = self.level.get_next_level()
        return next_level

    def resolve_current_avatar_head(self, info):
        try:
            avatar = StudentAvatar.objects.get(
                student=self,
                avatar__type_of='HEAD',
                in_use=True,
            ).avatar
        except StudentAvatar.DoesNotExist:
            avatar = None
        return avatar

    def resolve_current_avatar_accessories(self, info):
        try:
            avatar = StudentAvatar.objects.get(
                student=self,
                avatar__type_of='ACCESSORIES',
                in_use=True,
            ).avatar
        except StudentAvatar.DoesNotExist:
            avatar = None
        return avatar

    def resolve_current_avatar_clothes(self, info):
        try:
            avatar = StudentAvatar.objects.get(
                student=self,
                avatar__type_of='CLOTHES',
                in_use=True,
            ).avatar
        except StudentAvatar.DoesNotExist:
            avatar = None
        return avatar

    def resolve_current_avatar_pants(self, info):
        try:
            avatar = StudentAvatar.objects.get(
                student=self,
                avatar__type_of='PANTS',
                in_use=True,
            ).avatar
        except StudentAvatar.DoesNotExist:
            avatar = None
        return avatar

    def resolve_user(self, info):
        return self.user

    def resolve_last_week_coins(self, info, week_count=1):
        today = timezone.now()
        most_recent_monday = today - timedelta(days=(today.isoweekday()-1))
        start_date = most_recent_monday - timedelta(days=7*(week_count-1))
        account = self.coinWallet

        data = (BlockTransaction.objects.filter(account=account)
                .filter(date__range=(start_date, today))
                .annotate(day=TruncDay("date"))
                .values("day")
                .annotate(coins=Sum("amount"))
                .values("day", "coins")
                .order_by("date")
                )

        return data

    def resolve_today_coins(self, info):

        today=date.today()
        account = self.coinWallet

        data = BlockTransaction.objects\
                .filter(
                    account=account,
                    date=today)\
                .aggregate(coins=Sum("amount"))
                
        return data['coins']

    def resolve_last_week_questions(self, info, week_count=1):
        today = timezone.now()
        most_recent_monday = today - timedelta(days=(today.isoweekday()))
        start_date = most_recent_monday - timedelta(days=7*(week_count-1))
        data = (BlockQuestionPresentation.objects.filter(
            block_presentation__block__students=self
        )
            .filter(status="CORRECT")
            .filter(create_timestamp__range=(start_date, today))
            .annotate(day=TruncDay("create_timestamp"))
            .values("day")
            .annotate(questions=Count("id"))
            .values("day", "questions")
            .order_by("day")
        )

        return data

    def resolve_current_weekly_treasure_level(self, info):
        return self.current_weekly_treasure_level
    
    def resolve_total_questions_and_hits(self, info):

        result = BlockPresentation.all_objects\
            .filter(student=self)\
            .aggregate(
                total_questions_answered=Sum('total'),
                total_questions_hit=Sum('hits'))

        return {
            "total":result['total_questions_answered'] if result['total_questions_answered'] is not None else 0,
            "hits":result['total_questions_hit'] if result['total_questions_hit'] is not None else 0}


class StudentTopicMasterySchema(DjangoObjectType):
    class Meta:
        model = StudentTopicMastery
        fields = "__all__"


class StudentGradeSchema(DjangoObjectType):
    class Meta:
        model = StudentGrade
        fields = "__all__"


class StudentAchievementSchema(DjangoObjectType):
    class Meta:
        model = StudentAchievement
        fields = "__all__"


class StudentHomeworkSchema(DjangoObjectType):
    class Meta:
        model = StudentHomework
        fields = "__all__"

    result = graphene.Field(StudentHomeworkResultType)

    def resolve_result(self, info):
        result = self.result
        return {"hits": result['hits'], "total": result['total']}

    block_with_deactive = graphene.List(BlockSchema)

    def resolve_block_with_deactive(self, info):
        return Block.all_objects.filter(student_homework__id=self.pk).all()


class HonorRollWithCurrentGradeSchema(graphene.ObjectType):
    students = graphene.List(StudentSchema)
    grade = graphene.Int()


class Query(graphene.ObjectType):

    # ----------------- Student ----------------- #

    students = graphene.List(StudentSchema)
    student_by_id = graphene.Field(StudentSchema, id=graphene.ID())
    students_by_guardian_id = graphene.List(
        StudentSchema, guardian_id=graphene.ID())
    students_for_honor_roll_by_student_id = graphene.Field(
        HonorRollWithCurrentGradeSchema, student_id=graphene.ID(), scope=graphene.String())

    def resolve_students(root, info, **kwargs):
        # Querying a list
        return Student.objects.all()

    def resolve_student_by_id(root, info, id):
        # Querying a single question
        return Student.objects.get(pk=id)

    def resolve_students_by_guardian_id(root, info, guardian_id):
        # Querying a list
        student_list = [
            obj.student for obj in GuardianStudent.objects.filter(
                guardian_id=guardian_id)]
        return student_list


    # Return array of students with postion of current student in roll of the give scope
    def resolve_students_for_honor_roll_by_student_id(root, info, scope=None):

        # Get current student from token
        student = info.context.user.student

        balance_of_positive_movement = student.coinWallet.block_transaction_aggregate
        
        # querySet is not validated yet, don't hit database
        students_of_honor_roll = Student.objects\
            .annotate(
                amount_answer_question = Sum(
                    Case(
                        When(
                            coinWallet__movement__side=F('coinWallet__positive_side'), 
                            coinWallet__movement__comment="Answer the questions.",
                            then='coinWallet__movement__amount'),
                        output_field = DecimalField(),
                        default = 0)))\
            .order_by('-amount_answer_question')

        if student.classroom is not None:
            if scope == 'classroom':
                students_of_honor_roll = students_of_honor_roll.filter(classroom=student.classroom)
            elif scope == 'school':
                # if school kid
                if hasattr(student.classroom.teacherclassroom.teacher, 'schoolteacher'):
                    students_of_honor_roll = students_of_honor_roll.filter(
                            classroom__teacherclassroom__teacher__schoolteacher__school
                            =student.classroom.teacherclassroom.teacher.schoolteacher.school)
                else:
                    students_of_honor_roll = students_of_honor_roll\
                        .filter(pk=student.id)
        else: # if the student is not belonged to any classroom
            if scope != 'socrates':
                students_of_honor_roll = students_of_honor_roll.filter(pk=student.id)

        # Get current student position in the scope
        student_position_in_honor_roll = students_of_honor_roll\
            .filter(amount_answer_question__gte=balance_of_positive_movement)\
            .count()
        students_of_honor_roll_limit_by_5 = students_of_honor_roll[:5].all()

        students_of_honor_roll_limit_by_5_include_student = []
        index = -1
        for id, _student in enumerate(students_of_honor_roll_limit_by_5):
            students_of_honor_roll_limit_by_5_include_student.append(_student)
            if str(_student.id) == str(student.id):
                index = id
        if index < 0:
            students_of_honor_roll_limit_by_5_include_student[4] = student

        return HonorRollWithCurrentGradeSchema(
            students=students_of_honor_roll_limit_by_5_include_student,
            grade=student_position_in_honor_roll)

    # ----------------- StudentTopicMastery ----------------- #

    students_topic_mastery = graphene.List(StudentTopicMasterySchema)
    student_topic_mastery_by_id = graphene.Field(
        StudentTopicMasterySchema, id=graphene.ID())

    def resolve_students_topic_mastery(root, info, **kwargs):
        # Querying a list
        return StudentTopicMastery.objects.all()

    def resolve_student_topic_mastery_by_id(root, info, id):
        # Querying a single question
        return StudentTopicMastery.objects.get(pk=id)

    # ----------------- StudentGrade ----------------- #

    students_grade = graphene.List(StudentGradeSchema)
    student_grade_by_id = graphene.Field(
        StudentGradeSchema, id=graphene.ID())
    students_by_classroom_id = graphene.List(
        StudentSchema, classroom_id=graphene.ID())

    def resolve_students_grade(root, info, **kwargs):
        # Querying a list
        return StudentGrade.objects.all()

    def resolve_student_grade_by_id(root, info, id):
        # Querying a single question
        return StudentGrade.objects.get(pk=id)

    def resolve_students_by_classroom_id(root, info, classroom_id):
        # Querying a single question
        return Student.objects.filter(classroom_id=classroom_id)

    # ----------------- StudentAchievement ----------------- #

    students_achievement = graphene.List(StudentAchievementSchema)
    student_achievement_by_id = graphene.Field(
        StudentAchievementSchema, id=graphene.ID())

    def resolve_students_achievement(root, info, **kwargs):
        # Querying a list
        return StudentAchievement.objects.all()

    def resolve_student_achievement_by_id(root, info, id):
        # Querying a single question
        return StudentAchievement.objects.get(pk=id)
