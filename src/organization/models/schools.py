from django.db import models
from django.utils.text import slugify
from app.models import RandomSlugModel, TimestampModel, IsActiveModel
from payments.models import DiscountCode, Order
import datetime


class Group(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'group_'

    name = models.CharField(max_length=128, null=True)
    classroom = models.ForeignKey(
        'organization.Classroom', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class School(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'school_'
    SCHOOL_PUBLIC = 'PUBLIC'
    SCHOOL_PRIVATE = 'PRIVATE'
    SCHOOL_CHARTER = 'CHARTER'
    SCHOOL_CHOICES = (
        (SCHOOL_PUBLIC, 'Public'),
        (SCHOOL_PRIVATE, 'Private'),
        (SCHOOL_CHARTER, 'Charter'),
    )

    name = models.CharField(max_length=128, null=True)
    # slug = models.SlugField(editable=False)
    # internal_code = models.CharField(max_length=128, null=True)
    type_of = models.CharField(
        max_length=15, null=True,  choices=SCHOOL_CHOICES)

    # student_plan = models.ManyToManyField('plans.StudentPlan')
    # organization = models.ForeignKey(
    #     'organization.Organization', on_delete=models.PROTECT, null=True)
    zip = models.CharField(max_length=128, null=True)
    country = models.CharField(max_length=128, null=True)
    district = models.CharField(max_length=128, null=True)

    # student = models.ManyToManyField('students.Student', blank=True)
    # group = models.ManyToManyField('organization.Group', blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class SchoolPersonnel(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'school_personnel_'
    GENDER_MALE = 'MALE'
    GENDER_FEMALE = 'FEMALE'
    GENDER_OTHER = 'OTHER'
    GENDER_CHOICES = (
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
    )

    user = models.OneToOneField(
        'users.User',
        on_delete=models.PROTECT,
        null=True
    )

    first_name = models.CharField(max_length=128, null=True)
    last_name = models.CharField(max_length=128, null=True)
    gender = models.CharField(max_length=8, null=True, choices=GENDER_CHOICES)
    has_order = models.BooleanField(default=False)
    zip = models.CharField(max_length=128, null=True)
    country = models.CharField(max_length=128, null=True)
    coupon_code = models.ForeignKey(
        DiscountCode,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.first_name+' '+self.last_name


class AdministrativePersonnel(SchoolPersonnel):
    PREFIX = 'administrative_personnel_'
    pass


class Teacher(SchoolPersonnel):
    PREFIX = 'teacher_personnel_'

    CLASSROOM_LIMIT = 1
    pass


class Subscriber(SchoolPersonnel):
    PREFIX = 'subscriber_'
    pass


class SchoolSubscriber(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'subscriber_school_'

    subscriber = models.ForeignKey(
        Subscriber,
        on_delete=models.CASCADE,
    )
    school = models.OneToOneField(
        School,
        on_delete=models.CASCADE,
    )


class Classroom(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'classroom_'
    STUDENTS_LIMIT = 40
    name = models.CharField(max_length=128, null=True)
    grade = models.ForeignKey(
        'kb.Grade', on_delete=models.PROTECT, null=True)
    language = models.CharField(max_length=128, null=True)
    audience = models.ForeignKey(
        'audiences.Audience', on_delete=models.PROTECT)
    # school = models.ForeignKey(School, null=True, on_delete=models.PROTECT)
    # teacher = models.ForeignKey(Teacher, null=True, on_delete=models.PROTECT)
    enable_games = models.BooleanField(default=True)
    game_cost_percentage = models.IntegerField(default=100)
    time_zone_value = models.CharField(max_length=128, default="Etc/GMT")
    time_zone_offset = models.IntegerField(default=0)
    goal_coins_per_day = models.IntegerField(default=1000)
    monday_start = models.TimeField(
        null=True, editable=True, default=datetime.time(7, 0, 0))
    monday_end = models.TimeField(
        null=True, editable=True, default=datetime.time(17, 0, 0))
    tuesday_start = models.TimeField(
        null=True, editable=True, default=datetime.time(7, 0, 0))
    tuesday_end = models.TimeField(
        null=True, editable=True, default=datetime.time(17, 0, 0))
    wednesday_start = models.TimeField(
        null=True, editable=True, default=datetime.time(7, 0, 0))
    wednesday_end = models.TimeField(
        null=True, editable=True, default=datetime.time(17, 0, 0))
    thursday_start = models.TimeField(
        null=True, editable=True, default=datetime.time(7, 0, 0))
    thursday_end = models.TimeField(
        null=True, editable=True, default=datetime.time(17, 0, 0))
    friday_start = models.TimeField(
        null=True, editable=True, default=datetime.time(7, 0, 0))
    friday_end = models.TimeField(
        null=True, editable=True, default=datetime.time(17, 0, 0))
    saturday_start = models.TimeField(null=True, editable=True)
    saturday_end = models.TimeField(null=True, editable=True)
    sunday_start = models.TimeField(null=True, editable=True)
    sunday_end = models.TimeField(null=True, editable=True)

    @property
    def isEmpty(self):
        if (len(self.student_set.all()) > 0):
            return False
        else:
            return True


class TeacherClassroom(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'teacher_classroom_'
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
    )
    classroom = models.OneToOneField(
        Classroom,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    plan = models.ForeignKey(
        'plans.Plan',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    order_detail = models.ForeignKey(
        'payments.OrderDetail',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    cancel_reason = models.TextField(blank=True)
    is_cancel = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    expired_at = models.DateTimeField(null=True, blank=True)
    period = models.CharField(
        max_length=100,
        choices=(("MONTHLY", "Monthly"), ("YEARLY", "Yearly")),
        default="MONTHLY",
        null=True,
        blank=True,
    )
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)


class SchoolTeacher(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'school_teacher_'
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
    )
    teacher = models.OneToOneField(
        Teacher,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    plan = models.ForeignKey(
        'plans.Plan',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    order_detail = models.ForeignKey(
        'payments.OrderDetail',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    cancel_reason = models.TextField(blank=True)
    is_cancel = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    expired_at = models.DateTimeField(null=True, blank=True)
    period = models.CharField(
        max_length=100,
        choices=(("MONTHLY", "Monthly"), ("YEARLY", "Yearly")),
        default="MONTHLY",
        null=True,
        blank=True,
    )
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)


class SchoolAdministrativePersonnel(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'school_administrative_personnel_'
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
    )
    administrative_personnel = models.OneToOneField(
        AdministrativePersonnel,
        on_delete=models.CASCADE,
    )
    plan = models.ForeignKey(
        'plans.Plan',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    order_detail = models.ForeignKey(
        'payments.OrderDetail',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    cancel_reason = models.TextField(blank=True)
    is_cancel = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    expired_at = models.DateTimeField(null=True, blank=True)
    period = models.CharField(
        max_length=100,
        choices=(("MONTHLY", "Monthly"), ("YEARLY", "Yearly")),
        default="MONTHLY",
        null=True,
        blank=True,
    )
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
