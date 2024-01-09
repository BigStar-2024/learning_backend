import os
import sys
import threading

from django.contrib.auth import get_user_model
from django.db import transaction, DatabaseError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q
from api.models import profile
from emails.services import sendSignUpEmail
from graphql_jwt.shortcuts import create_refresh_token, get_token
from guardians.schema import GuardianSchema
from organization.schema import AdministrativePersonnelSchema, SubscriberSchema, TeacherSchema
# from graphql_auth.schema import UserQuery, MeQuery
# from graphql_auth import mutations
from students.models import Student
from guardians.models import Guardian, GuardianStudent
from payments.models import DiscountCode
from students.schema import StudentSchema
from users.schema import UserSchema, UserProfileSchema
from users.models import User
import graphene


# TODO: move to user mutations
class CreateUser(graphene.Mutation):
    user = graphene.Field(UserSchema)
    profile = graphene.Field(UserProfileSchema)
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=False)

    def mutate(self, info, username, password):
        user = get_user_model()(
            username=username,
        )
        user.set_password(password)
        user.save()

        profile_obj = profile.objects.get(user=user.id)
        token = get_token(user)
        refresh_token = create_refresh_token(user)

        return CreateUser(
            user=user,
            profile=profile_obj,
            token=token,
            refresh_token=refresh_token)


# TODO: move to guardian mutations
class CreateGuardian(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
    user = graphene.Field(UserSchema)
    profile = graphene.Field(UserProfileSchema)
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=False)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        coupon = graphene.String(required=True)
        language = graphene.String(required=False)

    def mutate(
            self,
            info,
            username,
            password,
            email,
            first_name,
            last_name,
            coupon,
            language='en-us'):
        try:
            with transaction.atomic():
                print('Creating parent.')
                user = get_user_model()(
                    username=username,
                    language=language,
                    first_name = first_name,
                    last_name = last_name,
                )
                user.set_password(password)
                if email is not None:
                    user.email = email
                user.save()
                guardian = Guardian(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                )
                guardian.save()
                print('New guardian created.')

                if coupon:
                    coupon = coupon.upper()

                    # Check coupon code existence
                    discount = DiscountCode.objects\
                        .filter(code=coupon)\
                        .filter(Q(for_who=DiscountCode.COUPON_FOR_ALL) | Q(for_who=DiscountCode.COUPON_FOR_GUARDIAN))\
                        .first()
                        
                    if discount is None:
                        raise Exception("Coupon code is not correct!")

                    if((not discount.expired_at) and discount.expired_at < timezone.now()):
                        discount.is_active = False
                        discount.save()
                        raise Exception("Your discount code had been expired!")
                    
                    # Register this coupon code to this guardian
                    discount.guardian_set.add(guardian)
                    print('Coupon code added to parent')

                if user.profile :
                    user.profile.role = "guardian"
                    user.profile.save()
                profile_obj = profile.objects.get(user=user.id)
                token = get_token(user)
                refresh_token = create_refresh_token(user)
                print('Finished guardian creation. Sending sign up email.')
                
                # Send email
                thread_send_mail = threading.Thread(
                    target=sendSignUpEmail, args=('guardian', email, user,))
                print('running thread: send mail')
                thread_send_mail.start()
                # sendSignUpEmail(customer=user, template_name="guardian", to_email=email)

                return CreateGuardian(
                    guardian=guardian,
                    user=user, profile=profile_obj,
                    token=token,
                    refresh_token=refresh_token
                )
        except (Exception, DatabaseError) as e:
            print('Rolling back changes.')
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


# TODO: move to guardian student mutations
class CreateGuardianStudent(graphene.Mutation):
    guardian_student = graphene.List('guardians.schema.GuardianStudentSchema')

    class Arguments:
        guardian = graphene.ID(required=True)
        students = graphene.List(graphene.NonNull(graphene.ID))

    def mutate(self, info, guardian, students):
        guardian = Guardian.objects.get(id=guardian)
        guardian_students = []

        for student_id in students:
            student = Student.objects.get(id=student_id)
            guardian_student = GuardianStudent(
                guardian=guardian,
                student=student
            )
            guardian_student.save()
            guardian_students.append(guardian_student)

        return CreateGuardianStudent(
            guardian_student=guardian_students,
        )


# TODO: move to guardian mutations
class ChangeUserNameEmailPassword(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
    user = graphene.Field(UserSchema)
    student = graphene.Field(StudentSchema)
    subscriber = graphene.Field(SubscriberSchema)
    teacher = graphene.Field(TeacherSchema)
    administrativepersonnel = graphene.Field(AdministrativePersonnelSchema)
    profile = graphene.Field(UserProfileSchema)
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        username = graphene.String(required=False)
        password = graphene.String(required=False)
        email = graphene.String(required=False)

    def mutate(self, info, username = None, password = None, email = None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Authentication Required')
        if username is not None:
            user.username = username
        if password is not None:
            user.set_password(password)
        if email is not None:
            user.email = email
        user.save()

        guardian = user.guardian if hasattr(user, "guardian") else None
        student = user.student if hasattr(user, "student") else None
        subscriber = user.schoolpersonnel.subscriber if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "subscriber") else None
        teacher = user.schoolpersonnel.teacher if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "teacher") else None
        administrativepersonnel = user.schoolpersonnel.administrativepersonnel if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "administrativepersonnel") else None

        profile_obj = profile.objects.get(user=user.id)
        token = get_token(user)
        refresh_token = create_refresh_token(user)
        return ChangeUserNameEmailPassword(
            guardian = guardian,
            student = student,
            subscriber = subscriber,
            teacher = teacher,
            administrativepersonnel = administrativepersonnel,
            user=user, profile=profile_obj,
            token=token,
            refresh_token=refresh_token
        )


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_guardian = CreateGuardian.Field()
    create_guardian_student = CreateGuardianStudent.Field()
    change_user_name_email_password = ChangeUserNameEmailPassword.Field()
    # register = mutations.Register.Field()
    # verify_account = mutations.VerifyAccount.Field()
    # resend_activation_email = mutations.ResendActivationEmail.Field()
    # send_password_reset_email = mutations.SendPasswordResetEmail.Field()
    # password_reset = mutations.PasswordReset.Field()

class WhoamiInput(graphene.ObjectType):
   user = graphene.Field(UserSchema)
   student = graphene.Field(StudentSchema)
   guardian = graphene.Field(GuardianSchema)
   subscriber = graphene.Field(SubscriberSchema)
   teacher = graphene.Field(TeacherSchema)
   administrativepersonnel = graphene.Field(AdministrativePersonnelSchema)

class Query(graphene.ObjectType):
    whoami = graphene.Field(WhoamiInput)
    users = graphene.List(UserSchema)

    def resolve_whoami(root, info, **kwargs):
        user = info.context.user
        data = {
            "user" : user,
            "student" : user.student if hasattr(user, "student") else None,
            "guardian": user.guardian if hasattr(user, "guardian") else None,
            "subscriber": user.schoolpersonnel.subscriber if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "subscriber") else None,
            "teacher": user.schoolpersonnel.teacher if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "teacher") else None,
            "administrativepersonnel": user.schoolpersonnel.administrativepersonnel if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "administrativepersonnel") else None,
        } 
        # TODO: Move to cronjob
        # if user.student:
        #     student = user.student
        #     now = datetime.now().date()
        #     delta = (
        #         now - student.int_period_start_at).total_seconds() / 3600 / 24
        #     bankBallance = student.bankWallet.balance
        #     interests = Interest.objects.filter(
        #         period__lte=delta, requireCoin__lte=bankBallance).order_by('-requireCoin')
        #     if(len(interests) > 0):
        #         amount = interests[0].amount
        #         BankMovement.objects.create(
        #             amount=amount,
        #             account=student.bankWallet,
        #             side=Account.SIDE_CHOICE_RIGHT_INTEREST)
        if user.is_anonymous:
            raise Exception('Authentication Failure')
        return data

    def resolve_users(root, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Authentication Failure')
        if user.profile.role != 'manager':
            raise Exception('Role Failure')
        return get_user_model().objects.all()
