import os
import random
from re import sub
import sys
import threading
from emails.services import sendSignUpEmail
import graphene
from django.contrib.auth import get_user_model
from django.db import transaction, DatabaseError
from graphene import ID
from avatars.models import Avatar, StudentAvatar
from block.models import BlockPresentation
from experiences.models import Battery
from organization.models.schools import SchoolAdministrativePersonnel, SchoolPersonnel, SchoolSubscriber, SchoolTeacher, Subscriber, TeacherClassroom
from users.schema import UserSchema, UserProfileSchema
from organization.schema import AdministrativePersonnelSchema, ClassroomSchema, SchoolPersonnelSchema, SchoolSchema, SubscriberSchema, TeacherSchema, GroupSchema
from organization.models import School, Group, Teacher, Classroom, AdministrativePersonnel
from graphql_jwt.shortcuts import create_refresh_token, get_token
from payments.models import DiscountCode
from kb.models.grades import Grade
from audiences.models import Audience
from users.models import User
from students.models import Student, StudentGrade
from students.schema import StudentSchema
from django.utils import timezone
from pytz import timezone as pytz_timezone
import datetime

from django.db.models import Sum, Count, F
from django.db.models import Q


class CreateTeacherInput(graphene.InputObjectType):
    email = graphene.String()
    name = graphene.String()
    last_name = graphene.String()
    password = graphene.String()
    gender = graphene.String()
    user_type = graphene.String()
    username = graphene.String()


class CreateTeacher(graphene.Mutation):
    """Create a user account for teacher API"""
    teacher = graphene.Field(TeacherSchema)
    user = graphene.Field(UserSchema)
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        zip = graphene.String(required=True)
        country = graphene.String(required=True)
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        coupon_code = graphene.String(required=False)

    def mutate(
        self,
        info,
        first_name,
        last_name,
        zip,
        country,
        email,
        password,
        username,
        coupon_code=None,
    ):

        try:
            with transaction.atomic():
                print('Creating individual teacher.')
                user = get_user_model()(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                )
                user.set_password(password)
                user.save()

                teacher = Teacher(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    zip=zip,
                    country=country,
                )

                teacher.save()
                print('New teacher created.')

                thread_send_mail = threading.Thread(
                    target=sendSignUpEmail, args=('teacher', email, user,))
                print('running thread: send mail')
                thread_send_mail.start()

                teacher.save()
                print('New teacher created.')
                
                # Send email
                # sendSignUpEmail(
                #     customer=user, template_name="teacher", to_email=email)

                print("before coupon code")
                if coupon_code:
                    coupon_code = coupon_code.upper()
                    discount = DiscountCode.objects.filter(code=coupon_code).filter(
                        Q(for_who=DiscountCode.COUPON_FOR_ALL) | Q(for_who=DiscountCode.COUPON_FOR_TEACHER))
                    if (discount.count() < 1):
                        raise Exception("Coupon code is not correct!")
                    teacher.coupon_code = discount[0]

                teacher.save()

                if user.profile:
                    user.profile.role = "teacher"
                    user.profile.save()

                token = get_token(user)
                refresh_token = create_refresh_token(user)

                print('Teacher register complete.')

                return CreateTeacher(
                    teacher=teacher,
                    user=user,
                    token=token,
                    refresh_token=refresh_token
                )

        except (Exception, DatabaseError) as e:
            print('Rolling back changes.')
            transaction.rollback()
            print('Done.')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class CreateClassroom(graphene.Mutation):
    """Create a classroom for a specific teacher depends on order API"""
    user = graphene.Field(UserSchema)
    classroom = graphene.Field(ClassroomSchema)
    teacher = graphene.Field(TeacherSchema)

    class Arguments:
        name = graphene.String(required=True)
        # grade_id = graphene.ID(required=True)
        # language = graphene.String(required=True)
        audience_id = graphene.ID(required=True)
        teacher_id = graphene.ID(required=False)

    def mutate(
        self,
        info,
        name,
        audience_id,
        teacher_id=None,
    ):

        try:
            with transaction.atomic():
                user = info.context.user
                role = user.profile.role
                if user.is_anonymous:
                    raise Exception('Authentication Required')
                if (user.schoolpersonnel is None and teacher_id is None):
                    raise Exception("You don't have permission!")
                elif (teacher_id is not None and not (role == "adminTeacher" or role == "subscriber")):
                    raise Exception("You don't have permission!")

                # grade = Grade.objects.get(pk=grade_id)
                audience = Audience.objects.get(pk=audience_id)

                teacher = user.schoolpersonnel.teacher if teacher_id is None else Teacher.objects.get(
                    pk=teacher_id)
                if (role == "adminTeacher"):
                    count = SchoolTeacher.objects.filter(
                        teacher=teacher, school__schooladministrativepersonnel=user.schoolpersonnel.administrativepersonnel.schooladministrativepersonnel).count()
                    if (count < 1):
                        raise Exception("You don't have permission!")
                elif (role == "subscriber"):
                    count = SchoolTeacher.objects.filter(
                        teacher=teacher, school__schoolsubscriber__subscriber=user.schoolpersonnel.subscriber).count()
                    if (count < 1):
                        raise Exception("You don't have permission!")

                classroom = Classroom(
                    name=name,
                    # grade=grade,
                    # language=language,
                    audience=audience,
                )
                # classroom.teacher = teacher
                classroom.save()

                # #------ If user is a admin Teacher or Subscriber, create Teacher Classroom depend on teacher classroom limit -S-----------#
                # if(not(teacher.has_order) and teacher.schoolteacher.order_detail):
                #     if TeacherClassroom.objects.filter(teacher = teacher, classroom__isnull = False).count() >= Teacher.CLASSROOM_LIMIT:
                #         raise Exception("The number of Classrooms has been exceeded! Please buy a new classroom")
                #     else:
                #         teacher_classrooms = TeacherClassroom.objects.filter(teacher = teacher, classroom__isnull = True)
                #         if(len(teacher_classrooms) < 1):
                #             raise Exception("The number of Classrooms has been exceeded! Please buy a new classroom")
                #         teacher_classrooms[0].classroom = classroom
                #         teacher_classrooms[0].save()
                # #------ If user is a admin Teacher or Subscriber, create Teacher Classroom depend on teacher classroom -E-----------#

                # #------ If user is a Teacher assing the classroom to available teacher_classrooms that is already created -S-----------#
                # elif(teacher.has_order):
                #     teacher_classrooms = TeacherClassroom.objects.filter(teacher = teacher, classroom = None)
                #     if(len(teacher_classrooms) < 1):
                #         raise Exception("The number of Classrooms has been exceeded! Please buy a new classroom")
                #     teacher_classrooms[0].classroom = classroom
                #     teacher_classrooms[0].save()
                # #------ If user is a Teacher assing the classroom to available teacher_classrooms that is already created -E-----------#
                teacher_classrooms = TeacherClassroom.objects.filter(
                    teacher=teacher, classroom=None)
                if (len(teacher_classrooms) < 1):
                    raise Exception(
                        "The number of Classrooms has been exceeded! Please buy a new classroom")
                teacher_classrooms[0].classroom = classroom
                teacher_classrooms[0].save()
                return CreateClassroom(
                    user=user,
                    classroom=classroom,
                    teacher=teacher
                )

        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class CreateClassroomToSchool(graphene.Mutation):
    """Create a classroom to school API"""
    user = graphene.Field(UserSchema)
    classroom = graphene.Field(ClassroomSchema)
    teacher = graphene.Field(TeacherSchema)

    class Arguments:
        name = graphene.String(required=True)
        teacher_id = graphene.ID(required=True)
        audience_id = graphene.ID(required=True)

    def mutate(
        self,
        info,
        name,
        audience_id,
        teacher_id,
    ):

        try:
            with transaction.atomic():
                user = info.context.user
                if user.is_anonymous:
                    raise Exception('Authentication Required')
                role = user.profile.role
                if (not (role == "adminTeacher" or role == "subscriber")):
                    raise Exception("You don't have permission!")
                teacher = Teacher.objects.get(pk=teacher_id)
                if (role == "adminTeacher"):
                    school = user.schoolpersonnel.administrativepersonnel.schooladministrativepersonnel.school
                    if len(SchoolTeacher.objects.filter(school=school, teacher=teacher) < 1):
                        raise Exception("Teacher is not your school's teacher")
                elif (role == "subscriber"):
                    school = teacher.schoolteacher.school
                    subscriber_me = user.schoolpersonnel.subscriber
                    print("school is ", school.id)
                    print("subscriber me is ", subscriber_me.id)
                    if len(SchoolSubscriber.objects.filter(school=school, subscriber=subscriber_me)) < 1:
                        raise Exception("Teacher is not your school's teacher")

                if TeacherClassroom.objects.filter(teacher=teacher, classroom__isnull=False).count() >= Teacher.CLASSROOM_LIMIT:
                    raise Exception(
                        "The number of teacher's classrooms has been exceeded")

                # grade = Grade.objects.get(pk=grade_id)
                audience = Audience.objects.get(pk=audience_id)

                classroom = Classroom(
                    name=name,
                    # grade=grade,
                    # language=language,
                    audience=audience,
                )
                # classroom.teacher = teacher
                classroom.save()

                teacher_classrooms = TeacherClassroom.objects.filter(
                    teacher=teacher, classroom__isnull=True)
                if (teacher_classrooms.count() < 1):
                    raise Exception(
                        "No available to create a new teacher classrooms")
                teacher_classrooms[0].classroom = classroom
                teacher_classrooms[0].save()
                return CreateClassroomToSchool(
                    user=user,
                    classroom=classroom,
                    teacher=teacher
                )

        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class CreateSchool(graphene.Mutation):
    """Create a school with user account for subscriber of school API"""
    user = graphene.Field(UserSchema)
    school = graphene.Field(SchoolSchema)
    subscriber = graphene.Field(SubscriberSchema)
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        district = graphene.String(required=True)
        type = graphene.String(required=True)
        zip = graphene.String(required=True)
        country = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        username = graphene.String(required=True)
        coupon_code = graphene.String(required=False)

    def mutate(
        self,
        info,
        name,
        first_name,
        last_name,
        district,
        type,
        zip,
        country,
        email,
        password,
        username,
        coupon_code=None
    ):

        try:
            with transaction.atomic():
                print('Creating a new school.')
                school = School(
                    name=name,
                    type_of=type,
                    zip=zip,
                    country=country,
                    district=district,
                )
                school.save()
                print('Creating a new user.')
                user = get_user_model()(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                )
                user.set_password(password)
                user.email = email
                user.save()
                print('Creating a new subscriber.')
                subscriber = Subscriber(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                )
                subscriber.save()

                # Checking coupon code.
                if coupon_code:
                    coupon = coupon_code.upper()

                    # Check coupon code existence
                    discount = DiscountCode.objects\
                        .filter(code=coupon)\
                        .filter(Q(for_who=DiscountCode.COUPON_FOR_ALL) | Q(for_who=DiscountCode.COUPON_FOR_SUBSCRIBER))\
                        .first()

                    if discount is None:
                        raise Exception("Coupon code is not correct!")

                    if ((not discount.expired_at) and discount.expired_at < timezone.now()):
                        discount.is_active = False
                        discount.save()
                        raise Exception("Your discount code had been expired!")

                    # Register coupon code to the teacher.
                    print('Adding Coupon to the subscriber.')
                    discount.schoolpersonnel_set.add(subscriber)

                    # discount = DiscountCode.objects.filter(code=coupon_code).filter(
                    #     Q(for_who=DiscountCode.COUPON_FOR_ALL) | Q(for_who=DiscountCode.COUPON_FOR_SUBSCRIBER))
                    # if (discount.count() < 1):
                    #     raise Exception("Coupon code is not correct!")
                    # subscriber.coupon_code = discount[0]
                # subscriber.save()

                SchoolSubscriber.objects.create(
                    subscriber=subscriber,
                    school=school
                )
                token = get_token(user)

                if user.profile:
                    user.profile.role = "subscriber"
                    user.profile.save()

                refresh_token = create_refresh_token(user)

                # Send email, should send sign up email after all is completed.
                print('Sending sign up email to ', email)
                # sendSignUpEmail(
                #     customer=user, template_name="subscriber", to_email=email)

                thread_send_mail = threading.Thread(
                    target=sendSignUpEmail, args=('subscriber', email, user,))
                thread_send_mail.start()
                return CreateSchool(
                    user=user,
                    school=school,
                    subscriber=subscriber,
                    token=token,
                    refresh_token=refresh_token,
                )

        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class AddSchool(graphene.Mutation):
    """Create a school and add it to a subscriber which is current logined subscriber user API"""
    school = graphene.Field(SchoolSchema)
    subscriber = graphene.Field(SubscriberSchema)

    class Arguments:
        name = graphene.String(required=True)
        district = graphene.String(required=True)
        type = graphene.String(required=True)
        zip = graphene.String(required=True)
        country = graphene.String(required=True)
        coupon_code = graphene.String(required=False)

    def mutate(
        self,
        info,
        name,
        district,
        type,
        zip,
        country,
        coupon_code=None,
    ):

        try:
            with transaction.atomic():
                user = info.context.user
                if user.is_anonymous:
                    raise Exception('Authentication Required')
                if user.schoolpersonnel.subscriber is None:
                    raise Exception(
                        "You don't have permission to add a school")
                subscriber = user.schoolpersonnel.subscriber

                school = School(
                    name=name,
                    type_of=type,
                    zip=zip,
                    country=country,
                    district=district,
                )
                school.save()

                if coupon_code:
                    discount = DiscountCode.objects.filter(code=coupon_code).filter(
                        Q(for_who=DiscountCode.COUPON_FOR_ALL) | Q(for_who=DiscountCode.COUPON_FOR_SUBSCRIBER))
                    if (discount.count() < 1):
                        raise Exception("Coupon code is not correct!")
                    subscriber.coupon_code = discount[0]
                    subscriber.save()

                SchoolSubscriber.objects.create(
                    subscriber=subscriber,
                    school=school
                )

                return AddSchool(
                    school=school,
                    subscriber=subscriber,
                )

        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class CreateTeachersInSchool(graphene.Mutation):
    """Create any number of the teachers necessary for the school and place them in the school API"""
    school = graphene.Field(SchoolSchema)

    class Arguments:
        teachers = graphene.List(CreateTeacherInput)
        school_id = graphene.ID()

    def mutate(
        self,
        info,
        teachers,
        school_id
    ):

        try:
            with transaction.atomic():
                user = info.context.user
                if user.is_anonymous:
                    raise Exception('Authentication Required')
                if not (user.profile.role == "subscriber" or user.profile.role == "adminTeacher"):
                    raise Exception("You don't have this permission!")

                school = School.objects.get(pk=school_id)
                if (user.profile.role == "subscriber"):
                    subscriber = school.schoolsubscriber.subscriber
                    if user.id != subscriber.user.id:
                        raise Exception(
                            "You don't have permission to control this school!")
                if (user.profile.role == "adminTeacher"):
                    if len(SchoolAdministrativePersonnel.objects.filter(school=school, administrative_personnel__user=user)) == 0:
                        raise Exception(
                            "You don't have permission to control this school!")

                available_school_teachers = SchoolTeacher.objects.filter(
                    school=school, teacher__isnull=True, order_detail__isnull=False)
                print(available_school_teachers)
                if len(available_school_teachers) < len(teachers):
                    raise Exception(
                        "Number of teachers are bigger than registe available teachers number")
                pointer = 0
                for available_school_teacher in available_school_teachers:
                    if pointer >= len(teachers):
                        break
                    teacher = teachers[pointer]
                # for teacher in teachers:
                    user = get_user_model()(
                        username=teacher.username,
                        first_name=teacher.name,
                        last_name=teacher.last_name
                    )
                    user.set_password(teacher.password)
                    user.email = teacher.email
                    user.save()
                    if (teacher.user_type == "Admin"):

                        # print("sap is ", sap)
                        admin = AdministrativePersonnel.objects.create(
                            # schooladministrativepe rsonnel = sap,
                            user=user,
                            first_name=teacher.name,
                            last_name=teacher.last_name,
                            gender=teacher.gender,
                        )
                        sap = SchoolAdministrativePersonnel.objects.create(
                            school=school,
                            order_detail=available_school_teacher.order_detail,
                            cancel_reason=available_school_teacher.cancel_reason,
                            is_cancel=available_school_teacher.is_cancel,
                            is_paid=available_school_teacher.is_paid,
                            expired_at=available_school_teacher.expired_at,
                            period=available_school_teacher.period,
                            administrative_personnel=admin,
                        )
                        available_school_teacher.hard_delete()
                    else:
                        teacher = Teacher.objects.create(
                            user=user,
                            first_name=teacher.name,
                            last_name=teacher.last_name,
                            gender=teacher.gender,
                        )

                        for i in range(Teacher.CLASSROOM_LIMIT):
                            TeacherClassroom.objects.create(teacher=teacher)

                        available_school_teachers[pointer].teacher = teacher
                        available_school_teachers[pointer].save()
                    pointer += 1

                return CreateTeachersInSchool(
                    school=school
                )

        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class UpdateClassroomSettings(graphene.Mutation):
    """Update classroom settings API"""
    classroom = graphene.Field(ClassroomSchema)
    user = graphene.Field(UserSchema)

    class Arguments:
        classroom_id = graphene.ID(required=True)
        # language = graphene.String()
        enable_game = graphene.Boolean(required=False)
        game_cost_percentage = graphene.Int(required=False)
        # time_zone_value = graphene.String()
        # time_zone_offset = graphene.Int()
        goal_coins_per_day = graphene.Int(required=False)
        # monday_start = graphene.Time()
        # monday_end = graphene.Time()
        # tuesday_start = graphene.Time()
        # tuesday_end = graphene.Time()
        # wednesday_start = graphene.Time()
        # wednesday_end = graphene.Time()
        # thursday_start = graphene.Time()
        # thursday_end = graphene.Time()
        # friday_start = graphene.Time()
        # friday_end = graphene.Time()
        # saturday_start = graphene.Time()
        # saturday_end = graphene.Time()
        # sunday_start = graphene.Time()
        # sunday_end = graphene.Time()

    def mutate(
        self,
        info,
        classroom_id,
        enable_game=None,
        game_cost_percentage=None,
        # monday_start,
        # monday_end,
        # tuesday_start,
        # tuesday_end,
        # wednesday_start,
        # wednesday_end,
        # thursday_start,
        # thursday_end,
        # friday_start,
        # friday_end,
        # saturday_start,
        # saturday_end,
        # sunday_start,
        # sunday_end,
        # time_zone_value,
        # time_zone_offset,
        goal_coins_per_day=None,
        # language=None,
    ):

        try:
            with transaction.atomic():
                user = info.context.user
                if not user.is_authenticated:
                    raise Exception('Authentication Required')
                if not (user.profile.role == "subscriber" or user.profile.role == "adminTeacher" or user.profile.role == "teacher"):
                    raise Exception("You don't have this permission!")
                classroom = Classroom.objects.get(pk=classroom_id)
                # classroom.language = language
                if enable_game is not None:
                    classroom.enable_games = enable_game
                # classroom.enable_games = enable_game
                if game_cost_percentage is not None:
                    classroom.game_cost_percentage = game_cost_percentage
                # classroom.time_zone_value = time_zone_value
                # classroom.time_zone_offset = time_zone_offset
                # classroom.monday_start = monday_start
                # classroom.monday_end = monday_end
                # classroom.tuesday_start = tuesday_start
                # classroom.tuesday_end = tuesday_end
                # classroom.wednesday_start = wednesday_start
                # classroom.wednesday_end = wednesday_end
                # classroom.thursday_start = thursday_start
                # classroom.thursday_end = thursday_end
                # classroom.friday_start = friday_start
                # classroom.friday_end = friday_end
                # classroom.saturday_start = saturday_start
                # classroom.saturday_end = saturday_end
                # classroom.sunday_start = sunday_start
                # classroom.sunday_end = sunday_end
                if goal_coins_per_day is not None:
                    classroom.goal_coins_per_day = goal_coins_per_day
                classroom.save()
                return UpdateClassroomSettings(
                    classroom=classroom,
                    user=user
                )

        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class ImportStudentToClassroom(graphene.Mutation):
    classroom = graphene.Field(ClassroomSchema)

    class Arguments:
        username = graphene.String()
        password = graphene.String()
        classroom_id = graphene.ID()

    def mutate(
        self,
        info,
        username,
        password,
        classroom_id,
    ):

        try:
            with transaction.atomic():
                user = info.context.user
                if user.is_anonymous:
                    raise Exception('Authentication Required')
                student_user = User.objects.get(username=username)
                student = student_user.student
                pwdChkResult = student_user.check_password(password)
                if (pwdChkResult == False):
                    raise Exception('Password of Student is wrong')
                classroom = Classroom.objects.get(pk=classroom_id)
                student.classroom = classroom
                student.audience = classroom.audience
                student.save()
                return ImportStudentToClassroom(
                    classroom=classroom
                )

        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class CreateStudentsInputs(graphene.InputObjectType):
    classroom_id = graphene.ID()
    grade_id = graphene.ID()
    name = graphene.String()
    last_name = graphene.String()
    password = graphene.String()
    username = graphene.String()


class CreateStudentToClassroom(graphene.Mutation):
    classroom = graphene.Field(ClassroomSchema)
    student = graphene.Field(StudentSchema)

    class Arguments:
        name = graphene.String()
        last_name = graphene.String()
        username = graphene.String()
        password = graphene.String()
        classroom_id = graphene.ID()
        grade_id = graphene.ID()

    def mutate(
        self,
        info,
        name,
        last_name,
        username,
        password,
        classroom_id,
        grade_id,
    ):

        try:
            with transaction.atomic():
                user = info.context.user
                if user.is_anonymous:
                    raise Exception('Authentication Required')

                classroom = Classroom.objects.get(pk=classroom_id)

                if user.profile.role == "teacher":
                    teacher = user.schoolpersonnel.teacher
                    if (TeacherClassroom.objects.filter(classroom=classroom, teacher=teacher).count() < 1):
                        raise Exception(
                            "You are a teacher but don't have permission to control this classroom!")
                elif user.profile.role == "subscriber":
                    subscriber = user.schoolpersonnel.subscriber
                    if (TeacherClassroom.objects.filter(classroom=classroom, teacher__schoolteacher__school__schoolsubscriber__subscriber=subscriber).count() < 1):
                        raise Exception(
                            "You are a subscriber but don't have permission to control this classroom!")
                elif user.profile.role == "adminTeacher":
                    print("here")
                    adminTeacher = user.schoolpersonnel.administrativepersonnel
                    if (TeacherClassroom.objects.filter(classroom=classroom, teacher__schoolteacher__school__schooladministrativepersonnel__administrative_personnel=adminTeacher).count() < 1):
                        raise Exception(
                            "You are a administrative but don't have permission to control this classroom!")
                else:
                    raise Exception(
                        "You don't have permission to control this classroom!")

                if (len(classroom.student_set.all()) >= Classroom.STUDENTS_LIMIT):
                    raise Exception(
                        "Number of students exceeded in this classroom")
                user = get_user_model()(
                    username=username,
                    first_name=name,
                    last_name=last_name,
                )
                user.set_password(password)
                user.save()

                student = Student(
                    first_name=name,
                    last_name=last_name,
                    full_name=name + ' ' + last_name,
                    user=user,
                    classroom=classroom,
                    audience=classroom.audience,
                )
                student.save()

                student.init_student_topic_mastery()
                student.init_student_topic_status()

                battery, new = Battery.objects.get_or_create(
                    student=student,
                )
                battery.save()

                # set default avatar
                accessories = Avatar.objects.filter(type_of="ACCESSORIES")
                heads = Avatar.objects.filter(type_of="HEAD")
                clothes = Avatar.objects.filter(type_of="CLOTHES")
                pants = Avatar.objects.filter(type_of="PANTS")

                list_avatar_items = [random.choice(accessories), random.choice(
                    heads), random.choice(clothes), random.choice(pants)]

                for avatar in list_avatar_items:
                    student_avatar = StudentAvatar.objects.create(
                        student_id=student.id, avatar_id=avatar.id)
                    avatar_type = avatar.type_of
                    StudentAvatar.objects.filter(
                        student=student,
                        avatar__type_of=avatar_type,
                        in_use=True).update(
                        in_use=False)
                    student_avatar.in_use = True
                    student_avatar.save()

                # set grade to student
                studentGrade = StudentGrade.objects.get_or_create(
                    student=student,
                    grade_id=grade_id
                )
                return CreateStudentToClassroom(
                    classroom=classroom,
                    student=student
                )

        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class CreateStudentsToClassroom(graphene.Mutation):
    classroom = graphene.Field(ClassroomSchema)

    class Arguments:
        students = graphene.List(CreateStudentsInputs)

    def mutate(
        self,
        info,
        students,
    ):

        try:
            with transaction.atomic():
                user_me = info.context.user
                if user_me.is_anonymous:
                    raise Exception('Authentication Required')

                for student_data in students:
                    classroom = Classroom.objects.get(
                        pk=student_data.classroom_id)
                    # print(student_data)
                    if user_me.profile.role == "teacher":
                        teacher = user_me.schoolpersonnel.teacher
                        if (TeacherClassroom.objects.filter(classroom=classroom, teacher=teacher).count() < 1):
                            raise Exception(
                                "You are a teacher but don't have permission to control this classroom!")
                    elif user_me.profile.role == "subscriber":
                        subscriber = user_me.schoolpersonnel.subscriber
                        if (TeacherClassroom.objects.filter(classroom=classroom, teacher__schoolteacher__school__schoolsubscriber__subscriber=subscriber).count() < 1):
                            raise Exception(
                                "You are a subscriber but don't have permission to control this classroom!")
                    elif user_me.profile.role == "adminTeacher":
                        adminTeacher = user_me.schoolpersonnel.administrativepersonnel
                        if (TeacherClassroom.objects.filter(classroom=classroom, teacher__schoolteacher__school__schooladministrativepersonnel__administrative_personnel=adminTeacher).count() < 1):
                            raise Exception(
                                "You are a administrative but don't have permission to control this classroom!")
                    else:
                        raise Exception(
                            "You don't have permission to control this classroom!")

                    if (len(classroom.student_set.all()) >= Classroom.STUDENTS_LIMIT):
                        raise Exception(
                            "Number of students exceeded in this classroom")
                    user = get_user_model()(
                        username=student_data.username,
                        first_name=student_data.name,
                        last_name=student_data.last_name,
                    )
                    user.set_password(student_data.password)
                    user.save()

                    student = Student(
                        first_name=student_data.name,
                        last_name=student_data.last_name,
                        full_name=student_data.name + ' ' + student_data.last_name,
                        user=user,
                        classroom=classroom,
                        audience=classroom.audience,
                    )
                    student.save()

                    battery, new = Battery.objects.get_or_create(
                        student=student,
                    )
                    battery.save()

                    # set default avatar
                    accessories = Avatar.objects.filter(type_of="ACCESSORIES")
                    heads = Avatar.objects.filter(type_of="HEAD")
                    clothes = Avatar.objects.filter(type_of="CLOTHES")
                    pants = Avatar.objects.filter(type_of="PANTS")

                    list_avatar_items = [random.choice(accessories), random.choice(
                        heads), random.choice(clothes), random.choice(pants)]

                    for avatar in list_avatar_items:
                        student_avatar = StudentAvatar.objects.create(
                            student_id=student.id, avatar_id=avatar.id)
                        avatar_type = avatar.type_of
                        StudentAvatar.objects.filter(
                            student=student,
                            avatar__type_of=avatar_type,
                            in_use=True).update(
                            in_use=False)
                        student_avatar.in_use = True
                        student_avatar.save()

                    studentGrade = StudentGrade.objects.get_or_create(
                        student=student,
                        grade_id=student_data.grade_id
                    )
                return CreateStudentToClassroom(
                    classroom=classroom,
                )

        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class RemoveStudentFromClassroom(graphene.Mutation):
    classroom = graphene.Field(ClassroomSchema)

    class Arguments:
        classroom_id = graphene.ID()
        student_id = graphene.ID()

    def mutate(
        self,
        info,
        classroom_id,
        student_id,
    ):

        try:
            with transaction.atomic():
                user = info.context.user
                if user.is_anonymous:
                    raise Exception('Authentication Required')

                student = Student.objects.get(pk=student_id)
                if (student.classroom is None):
                    raise Exception("This student doesn not have a classroom")
                if (str(student.classroom.id) != str(classroom_id)):
                    raise Exception('Classroom does not exist in this student')

                student.classroom = None
                student.save()

                classroom = Classroom.objects.get(pk=classroom_id)
                return CreateStudentToClassroom(
                    classroom=classroom,
                )

        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class CreateGroup(graphene.Mutation):
    group = graphene.Field(GroupSchema)
    teacher = graphene.Field(TeacherSchema)
    classroom = graphene.Field(ClassroomSchema)

    class Arguments:
        name = graphene.String()
        classroom_id = graphene.ID()
        studentIds = graphene.List(graphene.ID)

    def mutate(
        self,
        info,
        name,
        classroom_id,
        studentIds,
    ):

        try:
            with transaction.atomic():
                user = info.context.user
                if user.is_anonymous:
                    raise Exception('Authentication Required')
                if not (user.profile.role == "subscriber" or user.profile.role == "adminTeacher" or user.profile.role == "teacher"):
                    raise Exception("You don't have this permission!")
                classroom = Classroom.objects.get(pk=classroom_id)
                group = Group(
                    name=name,
                    classroom=classroom
                )
                group.save()
                for studentId in studentIds:
                    student = Student.objects.get(
                        pk=studentId, classroom=classroom)
                    group.student_set.add(student)
                return CreateGroup(
                    group=group,
                    teacher=classroom.teacherclassroom.teacher,
                    classroom=classroom
                )

        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class StudentWithCoinsSchema(graphene.ObjectType):
    student = graphene.Field(StudentSchema)
    coins_sum = graphene.Int()


class ClassroomReport(graphene.Mutation):
    coins_today = graphene.Int()
    goal_coins_per_day = graphene.Int()
    correct_questions_count_today = graphene.Int()
    correct_questions_count_yesterday = graphene.Int()
    coins_yesterday = graphene.Int()
    class_leaders_yesterday = graphene.List(StudentWithCoinsSchema)
    coins_all = graphene.Int()
    questions_all = graphene.Int()

    class Arguments:
        classroom_id = graphene.ID()

    def mutate(
        self,
        info,
        classroom_id,
    ):
        classroom = Classroom.objects.get(pk=classroom_id)

        #--------- convert timezone to classroom time zone and get today start and yesterday start in classroom timezone -S----------#
        timezone_value = classroom.time_zone_value
        now = timezone.now()
        now = now.astimezone(pytz_timezone(timezone_value))
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = (today_start - datetime.timedelta(1))
        #--------- convert timezone to classroom time zone and get today start and yesterday start in classroom timezone -E----------#

        query_set_block_presentations_from_yesterday = BlockPresentation.all_objects.filter(
            student__classroom=classroom).filter(update_timestamp__gt=yesterday_start)
        query_set_block_presentations_only_yesterday = query_set_block_presentations_from_yesterday.filter(
            update_timestamp__lte=today_start)
        query_set_block_presentations_only_today = query_set_block_presentations_from_yesterday.filter(
            update_timestamp__gt=today_start)
        result_yesterday_for_leaders = query_set_block_presentations_only_yesterday\
            .values('student')\
            .annotate(coins_sum=Sum('coins'))\
            .annotate(bonusCoins_sum=Sum('bonusCoins'))\
            .annotate(coinWithBonus_sum=F('coins_sum') + F('bonusCoins_sum'))\
            .order_by('-coins_sum')[:5]

        result_yesterday = query_set_block_presentations_only_yesterday.aggregate(
            Sum('bonusCoins'), Sum('coins'), Sum('hits'), Sum('total'))
        result_today = query_set_block_presentations_only_today.aggregate(
            Sum('bonusCoins'), Sum('coins'), Sum('hits'), Sum('total'))
        result_all = BlockPresentation.all_objects.filter(student__classroom=classroom).aggregate(
            Sum('bonusCoins'), Sum('coins'), Sum('hits'), Sum('total'))

        #----------replace student id to student schema in the leaders in the yesterday -S------#
        for key, result_yesterday_for_leader in enumerate(result_yesterday_for_leaders):
            result_yesterday_for_leaders[key]['coins_sum'] = result_yesterday_for_leaders[key]['coinWithBonus_sum']
            student_id = result_yesterday_for_leaders[key]['student']
            student = Student.objects.get(pk=student_id)
            result_yesterday_for_leaders[key]['student'] = student
        #----------replace student id to student schema in the leaders in the yesterday -E------#

        return ClassroomReport(

            coins_today=(result_today['coins__sum'] if result_today['coins__sum'] else 0) + (
                result_today['bonusCoins__sum'] if result_today['bonusCoins__sum'] else 0),
            goal_coins_per_day=classroom.goal_coins_per_day if classroom.goal_coins_per_day else 0,
            correct_questions_count_today=result_today['hits__sum'] if result_today['hits__sum'] else 0,
            correct_questions_count_yesterday=result_yesterday[
                'hits__sum'] if result_yesterday['hits__sum'] else 0,
            coins_yesterday=(result_yesterday['coins__sum'] if result_yesterday['coins__sum'] else 0) + (
                result_yesterday['bonusCoins__sum'] if result_yesterday['bonusCoins__sum'] else 0),
            class_leaders_yesterday=result_yesterday_for_leaders,
            coins_all=(result_all['coins__sum'] if result_all['coins__sum'] else 0) + (
                result_all['bonusCoins__sum'] if result_all['bonusCoins__sum'] else 0),
            questions_all=result_all['total__sum'] if result_all['total__sum'] else 0,
        )


class SchoolReport(graphene.Mutation):
    coins_today = graphene.Int()
    goal_coins_per_day = graphene.Int()
    correct_questions_count_today = graphene.Int()
    correct_questions_count_yesterday = graphene.Int()
    coins_yesterday = graphene.Int()
    school_leaders_yesterday = graphene.List(StudentWithCoinsSchema)
    coins_all = graphene.Int()
    questions_all = graphene.Int()

    class Arguments:
        school_id = graphene.ID()

    def mutate(
        self,
        info,
        school_id,
    ):
        print("start school")
        school = School.objects.get(pk=school_id)

        now = timezone.now()
        print(now)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        print("today")
        yesterday_start = (today_start - datetime.timedelta(1))
        print("yesterday")
        classrooms_aggregate = Classroom.objects.filter(
            teacherclassroom__teacher__schoolteacher__school=school).aggregate(Sum('goal_coins_per_day'))
        print("here classroom aggregate")

        query_set_block_presentations_from_yesterday = BlockPresentation.all_objects.filter(
            student__classroom__teacherclassroom__teacher__schoolteacher__school=school).filter(update_timestamp__gt=yesterday_start)
        query_set_block_presentations_only_yesterday = query_set_block_presentations_from_yesterday.filter(
            update_timestamp__lte=today_start)
        query_set_block_presentations_only_today = query_set_block_presentations_from_yesterday.filter(
            update_timestamp__gt=today_start)
        result_yesterday_for_leaders = query_set_block_presentations_only_yesterday.values('student').annotate(coins_sum=Sum(
            'coins')).annotate(bonusCoins_sum=Sum('coins')).annotate(coinWithBonus_sum=F('coins_sum') + F('coins')).order_by('-coins_sum')[:5]
        result_yesterday = query_set_block_presentations_only_yesterday.aggregate(
            Sum('bonusCoins'), Sum('coins'), Sum('hits'), Sum('total'))
        result_today = query_set_block_presentations_only_today.aggregate(
            Sum('bonusCoins'), Sum('coins'), Sum('hits'), Sum('total'))
        result_all = BlockPresentation.all_objects.filter(student__classroom__teacherclassroom__teacher__schoolteacher__school=school).aggregate(
            Sum('bonusCoins'), Sum('coins'), Sum('hits'), Sum('total'))

        #----------replace student id to student schema in the leaders in the yesterday -S------#
        for key, result_yesterday_for_leader in enumerate(result_yesterday_for_leaders):
            student_id = result_yesterday_for_leaders[key]['student']
            student = Student.objects.get(pk=student_id)
            result_yesterday_for_leaders[key]['student'] = student
        #----------replace student id to student schema in the leaders in the yesterday -E------#

        return SchoolReport(

            coins_today=(result_today['coins__sum'] if result_today['coins__sum'] else 0) + (
                result_today['bonusCoins__sum'] if result_today['bonusCoins__sum'] else 0),
            goal_coins_per_day=classrooms_aggregate[
                'goal_coins_per_day__sum'] if classrooms_aggregate['goal_coins_per_day__sum'] else 0,
            correct_questions_count_today=result_today['hits__sum'] if result_today['hits__sum'] else 0,
            correct_questions_count_yesterday=result_yesterday[
                'hits__sum'] if result_yesterday['hits__sum'] else 0,
            coins_yesterday=(result_yesterday['coins__sum'] if result_yesterday['coins__sum'] else 0) + (
                result_yesterday['bonusCoins__sum'] if result_yesterday['bonusCoins__sum'] else 0),
            school_leaders_yesterday=result_yesterday_for_leaders,
            coins_all=(result_all['coins__sum'] if result_all['coins__sum'] else 0) + (
                result_all['bonusCoins__sum'] if result_all['bonusCoins__sum'] else 0),
            questions_all=result_all['total__sum'] if result_all['total__sum'] else 0,
        )


class Mutation(graphene.ObjectType):
    create_teacher = CreateTeacher.Field()
    create_classroom = CreateClassroom.Field()
    create_classroom_to_school = CreateClassroomToSchool.Field()
    create_school = CreateSchool.Field()
    create_teachers_in_school = CreateTeachersInSchool.Field()
    update_classroom_settings = UpdateClassroomSettings.Field()
    import_student_to_classroom = ImportStudentToClassroom.Field()
    create_student_to_classroom = CreateStudentToClassroom.Field()
    create_students_to_classroom = CreateStudentsToClassroom.Field()
    create_group = CreateGroup.Field()
    remove_student_from_classroom = RemoveStudentFromClassroom.Field()
    classroom_report = ClassroomReport.Field()
    school_report = SchoolReport.Field()
    add_school = AddSchool.Field()
