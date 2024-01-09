from ipaddress import v4_int_to_packed
from django.db import models
from django.db.models import Sum, Q
from app.models import TimestampModel, UUIDModel, IsActiveModel
from experiences.models import Level
from engine.models import TopicMasterySettings
from block.models import Block, BlockPresentation, BlockQuestionPresentation, BlockTransaction
from kb.models import areas_of_knowledge
from kb.models.topics import GradePrerequisite, Topic
from organization.models.schools import AdministrativePersonnel, Subscriber, Teacher
from treasuretrack.models import WeeklyTreasureLevel
from decimal import Decimal
from django.utils import timezone
from django.contrib import admin
from django.core.exceptions import MultipleObjectsReturned
from datetime import date, timedelta

TYPE_ACCESSORIES = 'ACCESSORIES'
TYPE_HEAD = 'HEAD'
TYPE_CLOTHES = 'CLOTHES'
TYPE_PANTS = 'PANTS'


class StudentTopicStatus(TimestampModel):
    class Status(models.TextChoices):
        BLOCKED = 'B', 'Blocked'
        PREVIEW = 'P', 'Preview'
        AVAILABLE = 'A', 'Available'

    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    topic = models.ForeignKey(
        'kb.Topic',
        on_delete=models.CASCADE,
        related_name='status'
    )
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.BLOCKED,
    )


class StudentTopicMastery(TimestampModel, UUIDModel):
    PREFIX = 'student_topic_mastery_'

    MASTERY_LEVEL_NOT_PRACTICED = 'NP'
    MASTERY_LEVEL_NOVICE = 'N'
    MASTERY_LEVEL_COMPETENT = 'C'
    MASTERY_LEVEL_MASTER = 'M'

    MASTERY_LEVEL_CHOICES = (
        (MASTERY_LEVEL_NOT_PRACTICED, 'Not practiced'),
        (MASTERY_LEVEL_NOVICE, 'Novice'),
        (MASTERY_LEVEL_COMPETENT, 'Competent'),
        (MASTERY_LEVEL_MASTER, 'Master')
    )

    # FK's
    topic = models.ForeignKey(
        'kb.Topic',
        on_delete=models.PROTECT,
        related_name='mastery',
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.PROTECT,
    )

    # Attributes
    mastery_level = models.CharField(
        max_length=3,
        choices=MASTERY_LEVEL_CHOICES,
        default='NP'
    )

    @property
    def status(self):
        try:
            status = StudentTopicStatus.objects.get(
                topic=self.topic, student=self.student).status
        except StudentTopicStatus.DoesNotExist:
            status = None
        except MultipleObjectsReturned:
            status = StudentTopicStatus.objects.filter(topic=self.topic, student=self.student).first()
        return status

    @property
    def grade(self):
        try:
            # print(dir(self.topic))
            grade = self.topic.topicgrade_set.all()[0].grade
        except Exception as e:
            grade = None
        return grade

    @property
    @admin.display(description='Prerequsites')
    def topic_prerequsite_str(self):
        return self.topic.prerequisites_str


class Student(TimestampModel, UUIDModel, IsActiveModel):
    GENDER_MALE = 'MALE'
    GENDER_FEMALE = 'FEMALE'
    GENDER_OTHER = 'OTHER'
    GENDER_CHOICES = (
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
    )

    PREFIX = 'student_'

    user = models.OneToOneField(
        'users.User',
        on_delete=models.PROTECT,
        null=True
    )
    first_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=True, blank=True)
    full_name = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        editable=False)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=8, null=True, choices=GENDER_CHOICES)
    points = models.IntegerField(default=0)
    int_period_start_at = models.DateField(auto_now_add=True)
    student_plan = models.ManyToManyField('plans.StudentPlan')
    active_student_plan = models.ForeignKey(
        'plans.StudentPlan',
        related_name="active_student_plan",
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    group = models.ManyToManyField('organization.Group', blank=True)
    active_group = models.ForeignKey(
        'organization.Group',
        related_name="active_group",
        on_delete=models.PROTECT,
        blank=True,
        null=True)
    level = models.ForeignKey(
        'experiences.Level',
        on_delete=models.PROTECT,
        null=True)
    audience = models.ForeignKey(
        'audiences.Audience',
        on_delete=models.PROTECT,
    )
    is_new = models.BooleanField(default=True)
    classroom = models.ForeignKey(
        'organization.Classroom',
        on_delete=models.CASCADE,
        blank=True,
        null=True)

    def current_age(self):
        today = datetime.date.today()
        birthDate = self.dob

        if self.dob is not None:
            age = (
                today.year
                - birthDate.year
                - (
                    (today.month, today.day) < (birthDate.month, birthDate.day)
                )
            )
        else:
            age = None
            return age

    @property
    def get_full_name(self):
        return (self.first_name if self.first_name else ' ') + \
            ' ' + (self.last_name if self.last_name else ' ')

    @property
    def get_active_audience(self):
        # return self.active_group.grade.audience if (self.active_group) else self.audience
        return self.active_group.grade.audience if (self.active_group) else None

    @property
    def get_level_number(self):
        return int(self.level.name.split("_")[1]) if (self.level.name) else 0

    @property
    def grade(self):

        student_grade = StudentGrade.objects.filter(
            student_id=self.id, is_active=True).order_by("-create_timestamp")
        if student_grade.count() != 0:
            return student_grade[0].grade
        return

    @property
    def current_weekly_treasure_level(self):
        today = timezone.now().date()
        all_levels = WeeklyTreasureLevel.objects.all()
        total_coins = BlockTransaction.objects.filter(
            account=self.coinWallet,
            date=today
        ).aggregate(
            Sum("amount")
        )["amount__sum"] or 0

        for level in all_levels:
            if total_coins < level.coins_required:
                return level.get_previous_level()
            else:
                total_coins -= level.coins_required

        return all_levels.last()

    @property
    def current_total_question(self):
        return 0

    @property
    def current_total_accurate(self):
        return 0

    @property
    def thisweek_correct_questions(self):
        today = timezone.now()
        most_recent_monday = today - timedelta(days=(today.isoweekday()))

        result = BlockPresentation.all_objects\
            .filter(
                student=self,
                create_timestamp__range=(most_recent_monday, today)
                )\
            .aggregate(
                total_questions_hit=Sum('hits'))

        return result['total_questions_hit'] if result['total_questions_hit'] is not None else 0

    def init_student_topic_mastery(self):
        from plans.models import GuardianStudentPlan
        from kb.models import AreaOfKnowledge
        try:
            available_aoks = GuardianStudentPlan.objects.get(
                student=self).subject.all()
        except GuardianStudentPlan.DoesNotExist:
            audience = self.get_active_audience
            available_aoks = AreaOfKnowledge.objects.filter(audience=audience)

        grade = self.grade

        for aok in available_aoks:
            topics = aok.topic_set.all()
            try:
                grade_prerequisite = GradePrerequisite.objects.get(
                    area_of_knowledge=aok,
                    grade=grade,
                )
            except GradePrerequisite.DoesNotExist:
                grade_prerequisite = None
            if grade_prerequisite:
                competence_topics = grade_prerequisite.competence.all()
                mastery_topics = grade_prerequisite.mastery.all()
                np_topics = topics.difference(
                    competence_topics,
                    mastery_topics
                )
                for topic in competence_topics:
                    topic_mastery, new = StudentTopicMastery.objects.get_or_create(
                        student=self,
                        topic=topic,
                        # mastery_level='C',
                    )
                    topic_mastery.mastery_level = 'C'
                    topic_mastery.save()
                for topic in mastery_topics:
                    topic_mastery, new = StudentTopicMastery.objects.get_or_create(
                        student=self,
                        topic=topic,
                        # mastery_level='M',
                    )
                    topic_mastery.mastery_level = 'M'
                    topic_mastery.save()
                for topic in np_topics:
                    topic_mastery, new = StudentTopicMastery.objects.get_or_create(
                        student=self,
                        topic=topic,
                    )
                    topic_mastery.save()
            else:
                for topic in topics:
                    topic_mastery, new = StudentTopicMastery.objects.get_or_create(
                        student=self,
                        topic=topic,
                    )
                    topic_mastery.save()

    def init_student_topic_mastery_specific_aok(self, aok_id):
        from plans.models import GuardianStudentPlan
        from kb.models import AreaOfKnowledge
        # try:
        available_aoks = AreaOfKnowledge.objects.filter(
                id=aok_id).all()
        # except GuardianStudentPlan.DoesNotExist:
        #     audience = self.get_active_audience
        #     available_aoks = AreaOfKnowledge.objects.filter(audience=audience)

        grade = self.grade

        for aok in available_aoks:
            topics = aok.topic_set.all()
            try:
                grade_prerequisite = GradePrerequisite.objects.get(
                    area_of_knowledge=aok,
                    grade=grade,
                )
            except GradePrerequisite.DoesNotExist:
                grade_prerequisite = None
            if grade_prerequisite:
                competence_topics = grade_prerequisite.competence.all()
                mastery_topics = grade_prerequisite.mastery.all()
                np_topics = topics.difference(
                    competence_topics,
                    mastery_topics
                )
                for topic in competence_topics:
                    topic_mastery, new = StudentTopicMastery.objects.get_or_create(
                        student=self,
                        topic=topic,
                        # mastery_level='C',
                    )
                    if (new):
                        topic_mastery.mastery_level = 'C'
                        topic_mastery.save()
                for topic in mastery_topics:
                    topic_mastery, new = StudentTopicMastery.objects.get_or_create(
                        student=self,
                        topic=topic,
                        # mastery_level='M',
                    )
                    if (new):
                        topic_mastery.mastery_level = 'M'
                        topic_mastery.save()
                for topic in np_topics:
                    topic_mastery, new = StudentTopicMastery.objects.get_or_create(
                        student=self,
                        topic=topic,
                    )
                    if (new):
                        topic_mastery.save()
            else:
                for topic in topics:
                    topic_mastery, new = StudentTopicMastery.objects.get_or_create(
                        student=self,
                        topic=topic,
                    )
                    if (new):
                        topic_mastery.save()

    def update_student_topic_mastery(self, topic):
        mastery_settings, new = TopicMasterySettings.objects.get_or_create(
            topic=topic
        )
        total_correct = 0
        sample_size = mastery_settings.sample_size
        mastery_percentage = mastery_settings.mastery_percentage / 100
        competence_percentage = mastery_settings.competence_percentage / 100
        # Get last N questions from topic sorted by date
        last_questions = BlockQuestionPresentation.all_objects.filter(
            block_presentation__student=self,
            topic=topic
        ).order_by('-create_timestamp')[:sample_size]
        for question in last_questions:
            if question.is_correct:
                total_correct += 1
        if total_correct == 0:
            mastery_level = 'NP'
        elif total_correct < sample_size * mastery_percentage * competence_percentage:
            mastery_level = 'N'
        elif total_correct < sample_size * mastery_percentage:
            mastery_level = 'C'
        else:
            mastery_level = 'M'
        # print(StudentTopicMastery.objects.filter(student=self, topic=topic))
        student_topic_mastery, new = StudentTopicMastery.objects.get_or_create(
            student=self, topic=topic, )
        student_topic_mastery.mastery_level = mastery_level
        student_topic_mastery.save()

    def init_student_topic_status(self):
        from plans.models import GuardianStudentPlan
        from kb.models import AreaOfKnowledge
        try:
            available_aoks = GuardianStudentPlan.objects.get(
                student=self).subject.all()
        except GuardianStudentPlan.DoesNotExist:
            audience = self.get_active_audience
            available_aoks = AreaOfKnowledge.objects.filter(audience=audience)

        for aok in available_aoks:
            topics = aok.topic_set.all()
            for topic in topics:
                if topic.prerequisites is None:
                    status = 'A'
                else:
                    prerequisites = topic.prerequisites
                    prerequisites_mastery = []
                    for prerequisite in prerequisites:
                        prerequisites_mastery.append(
                            prerequisite.mastery_level(self)
                        )
                    if 'NP' in prerequisites_mastery:
                        status = 'B'
                    elif 'N' in prerequisites_mastery:
                        status = 'B'
                    elif 'C' in prerequisites_mastery:
                        status = 'P'
                    else:
                        status = 'A'
                topic_status, new = StudentTopicStatus.objects.get_or_create(
                    student=self,
                    topic=topic,
                )
                topic_status.status = status
                topic_status.save()

    def init_student_topic_status_specific_aok(self, aok_id):
        from plans.models import GuardianStudentPlan
        from kb.models import AreaOfKnowledge
        try:
            available_aoks = AreaOfKnowledge.objects.filter(
                id=aok_id)
        except GuardianStudentPlan.DoesNotExist:
            audience = self.get_active_audience
            available_aoks = AreaOfKnowledge.objects.filter(audience=audience)

        for aok in available_aoks:
            topics = aok.topic_set.all()
            for topic in topics:
                if topic.prerequisites is None:
                    status = 'A'
                else:
                    prerequisites = topic.prerequisites
                    prerequisites_mastery = []
                    for prerequisite in prerequisites:
                        prerequisites_mastery.append(
                            prerequisite.mastery_level(self)
                        )
                    if 'NP' in prerequisites_mastery:
                        status = 'B'
                    elif 'N' in prerequisites_mastery:
                        status = 'B'
                    elif 'C' in prerequisites_mastery:
                        status = 'P'
                    else:
                        status = 'A'
                topic_status, new = StudentTopicStatus.objects.get_or_create(
                    student=self,
                    topic=topic,
                )
                if (new):
                    topic_status.status = status
                    topic_status.save()

    def update_student_topic_status(self, aok):
        # topics = aok.topic_set.all()

        topics = aok.topic_set.all()
        for topic in topics:
            if topic.prerequisites is None:
                status = 'A'
            else:
                prerequisites = topic.prerequisites
                prerequisites_mastery = []
                for prerequisite in prerequisites:
                    prerequisites_mastery.append(
                        prerequisite.mastery_level(self)
                    )
                if 'NP' in prerequisites_mastery:
                    status = 'B'
                elif 'N' in prerequisites_mastery:
                    status = 'B'
                elif 'C' in prerequisites_mastery:
                    status = 'P'
                else:
                    status = 'A'

            # topic_status, created = StudentTopicStatus.objects.update_or_create(
            #     student=self, 
            #     topic=topic, 
            #     status=status)

            try:
                topic_status, new = StudentTopicStatus.objects.get_or_create(
                    student=self,
                    topic=topic,
                )
            except MultipleObjectsReturned:
                topic_status = StudentTopicStatus.objects.filter(student=self,topic=topic).first()

            topic_status.status = status
            topic_status.save()

    def import_new_topic_mastery(self):
        from plans.models import GuardianStudentPlan
        from kb.models import AreaOfKnowledge
        try:
            available_aoks = GuardianStudentPlan.objects.get(
                student=self).subject.all()

        except GuardianStudentPlan.DoesNotExist:
            # If student is from teacher,
            audience = self.audience
            available_aoks = AreaOfKnowledge.objects.filter(Q(audience=audience) | Q(audience__standard_code='US'))
        grade = self.grade

        topics_in_mastery = Topic.objects.filter(
            area_of_knowledge__in=available_aoks, mastery__student=self).values_list('pk', flat=True)
        topics_without_status = Topic.objects.filter(
            area_of_knowledge__in=available_aoks).exclude(pk__in=topics_in_mastery)

        if (topics_without_status.count() < 1):
            return

        for aok in available_aoks:
            topics = topics_without_status.filter(area_of_knowledge=aok)

            try:
                grade_prerequisite = GradePrerequisite.objects.get(
                    area_of_knowledge=aok,
                    grade=grade,
                )
            except GradePrerequisite.DoesNotExist:
                grade_prerequisite = None
            if grade_prerequisite:
                competence_topics = grade_prerequisite.competence.all()
                mastery_topics = grade_prerequisite.mastery.all()
                np_topics = topics.difference(
                    competence_topics,
                    mastery_topics
                )
                for topic in competence_topics:
                    topic_mastery, new = StudentTopicMastery.objects.get_or_create(
                        student=self,
                        topic=topic,
                    )
                    if (new):
                        topic_mastery.mastery_level = 'C'
                    topic_mastery.save()
                for topic in mastery_topics:
                    topic_mastery, new = StudentTopicMastery.objects.get_or_create(
                        student=self,
                        topic=topic,
                    )
                    if (new):
                        topic_mastery.mastery_level = 'M'
                    topic_mastery.save()
                for topic in np_topics:
                    topic_mastery, new = StudentTopicMastery.objects.get_or_create(
                        student=self,
                        topic=topic,
                    )
                    topic_mastery.save()
            else:
                for topic in topics:
                    topic_mastery, new = StudentTopicMastery.objects.get_or_create(
                        student=self,
                        topic=topic,
                    )
                    topic_mastery.save()

    def import_new_topic_status(self):
        from plans.models import GuardianStudentPlan
        from kb.models import AreaOfKnowledge

        try:
            available_aoks = GuardianStudentPlan.objects.get(
                student=self).subject.all()
        except GuardianStudentPlan.DoesNotExist:
            audience = self.audience
            available_aoks = AreaOfKnowledge.objects.filter(Q(audience=audience) | Q(audience__standard_code='US'))
        # grade = self.grade

        topics_in_status = Topic.objects.filter(
            area_of_knowledge__in=available_aoks, status__student=self).values_list('pk', flat=True)
        topics_without_status = Topic.objects.filter(
            area_of_knowledge__in=available_aoks).exclude(pk__in=topics_in_status)

        if (topics_without_status.count() < 1):
            return

        print("Passed ...")

        for aok in available_aoks:
            topics = aok.topic_set.all()
            topics = topics_without_status.filter(area_of_knowledge=aok)
            # print(aok)
            # print(topics)
            for topic in topics:
                if topic.prerequisites is None:
                    status = 'A'
                else:
                    prerequisites = topic.prerequisites
                    prerequisites_mastery = []
                    for prerequisite in prerequisites:
                        prerequisites_mastery.append(
                            prerequisite.mastery_level(self)
                        )
                    if 'NP' in prerequisites_mastery:
                        status = 'B'
                    elif 'N' in prerequisites_mastery:
                        status = 'B'
                    elif 'C' in prerequisites_mastery:
                        status = 'P'
                    else:
                        status = 'A'
                topic_status, new = StudentTopicStatus.objects.get_or_create(
                    student=self,
                    topic=topic,
                )
                if (new):
                    topic_status.status = status
                topic_status.save()

    def import_new_topic(self):
        print("starting import new topic")
        self.import_new_topic_mastery()
        self.import_new_topic_status()
        print("finish")

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.full_name = self.get_full_name

        if self.pk is None:
            from wallets.models import CoinWallet
            from experiences.models import Battery
            super().save(*args, **kwargs)
            coin_wallet, cw_new = CoinWallet.objects.get_or_create(
                student=self,
                name=self.user.username
            )
            coin_wallet.save()

            battery, new = Battery.objects.get_or_create(
                student=self,
            )
            battery.save()

            from bank.models import BankWallet
            bank_account, ba_new = BankWallet.objects.get_or_create(
                student=self,
                name=self.user.username
            )
            bank_account.save()

            if self.level is None:
                current_level = Level.objects.get(amount=1)
                self.level = current_level

            # No need to init, will be done in the thread, this tooks much time to register a new kid for parent
            # self.init_student_topic_mastery()
            # self.init_student_topic_status()

            self.is_new = True

        return super(Student, self).save(*args, **kwargs)


class StudentGrade(TimestampModel, UUIDModel, IsActiveModel):
    PREFIX = 'student_grade_'
    grade = models.ForeignKey('kb.Grade', on_delete=models.PROTECT, null=True)
    student = models.ForeignKey(
        'students.Student', on_delete=models.PROTECT, null=True)
    is_finished = models.IntegerField(null=True)
    percentage = models.FloatField(null=True)
    complete_date = models.DateField(null=True, blank=True)


class StudentAchievement(TimestampModel, UUIDModel, IsActiveModel):
    PREFIX = 'student_achievement_'
    achivement = models.ForeignKey(
        'achievements.Achievement', on_delete=models.PROTECT, null=True)
    student = models.ForeignKey(
        'students.Student', on_delete=models.PROTECT, null=True)
    is_liberate = models.IntegerField(null=True)
    liberation_date = models.DateField(null=True, blank=True)


class StudentHomework(TimestampModel, UUIDModel, IsActiveModel):
    PREFIX = 'student_homework'
    HOMEWORK_DONE = 'Done'
    HOMEWORK_PENDING = 'Pending'
    HOMEWORK_EXPIRED = 'Expired'

    HOMEWORK_STATUS_SET = (
        (HOMEWORK_DONE, 'Done'),
        (HOMEWORK_PENDING, 'Pending'),
        (HOMEWORK_EXPIRED, 'Expired'),
    )
    name = models.CharField(max_length=128, null=True, blank=True, )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=False)
    number_of_questions = models.IntegerField(null=False, default=10)
    start_at = models.DateTimeField(editable=True, null=True, blank=True)
    end_at = models.DateTimeField(editable=True, null=True, blank=True)
    status = models.CharField(
        default=HOMEWORK_PENDING,
        choices=HOMEWORK_STATUS_SET,
        max_length=16,
    )
    assigned_teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, null=True, blank=True)
    assigned_subscriber = models.ForeignKey(
        Subscriber, on_delete=models.CASCADE, null=True, blank=True)
    assigned_administrative = models.ForeignKey(
        AdministrativePersonnel, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def result(self):
        blocks = Block.all_objects.filter(student_homework__id=self.pk).all()
        hits = 0
        total = 0
        for block in blocks:

            block_presentations = BlockPresentation.all_objects.filter(
                block=block).all()
            for block_presentation in block_presentations:
                hits += block_presentation.hits
                total += block_presentation.total
        return {"hits": hits, "total": total}
