import os
import sys
from this import s
import graphene
from django.db import transaction, DatabaseError
from guardians.models import Guardian
from organization.models.schools import School, SchoolSubscriber, SchoolTeacher, Subscriber, TeacherClassroom
from organization.schema import AdministrativePersonnelSchema, SchoolSchema, SubscriberSchema, TeacherSchema
from payments import services
from payments.card import Card
from payments.schema import PaymentMethodSchema
from plans.models import GuardianStudentPlan
from students.schema import StudentSchema
from .models import Order, OrderDetail, PaymentHistory, PaymentMethod
from users.models import User
from django.utils import timezone
import payments.services as payment_services
import datetime


class OrderDetailInput(graphene.InputObjectType):
    plan_id = graphene.ID()
    quantity = graphene.Int()
    period = graphene.String()


# Create new order
class CreateOrder(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
    teacher = graphene.Field('organization.schema.TeacherSchema')
    school = graphene.Field('organization.schema.SchoolSchema')
    order = graphene.Field('payments.schema.OrderSchema')
    status = graphene.String()
    url_redirect = graphene.String()

    class Arguments:
        guardian_id = graphene.ID(required=False)
        teacher_id = graphene.ID(required=False)
        school_id = graphene.ID(required=False)
        payment_method = graphene.String(required=True)
        order_detail_input = graphene.List(OrderDetailInput)
        return_url = graphene.String(required=True)
        card_first_name = graphene.String(required=False)
        card_last_name = graphene.String(required=False)
        card_number = graphene.String(required=False)
        card_exp_month = graphene.String(required=False)
        card_exp_year = graphene.String(required=False)
        card_cvc = graphene.String(required=False)
        address1 = graphene.String(required=False)
        address2 = graphene.String(required=False)
        city = graphene.String(required=False)
        state = graphene.String(required=False)
        post_code = graphene.String(required=False)
        country = graphene.String(required=False)
        phone = graphene.String(required=False)

    def mutate(
            self,
            info,
            payment_method,
            order_detail_input,
            return_url,
            guardian_id=None,
            school_id=None,
            teacher_id=None,
            card_first_name=None,
            card_last_name=None,
            card_number=None,
            card_exp_month=None,
            card_exp_year=None,
            card_cvc=None,
            address1=None,
            address2=None,
            city=None,
            state=None,
            post_code=None,
            country=None,
            phone=None
    ):
        if guardian_id is not None:
            user = User.objects.get(guardian__id=guardian_id)
        elif teacher_id is not None:
            user = User.objects.get(schoolpersonnel__teacher__id=teacher_id)
        elif school_id is not None:
            user = SchoolSubscriber.objects.get(
                school_id=school_id).subscriber.user
        try:
            # with transaction.atomic():
            sub_total = 0
            discount = 0
            total = 0
            create_order_resp = services.create_order(
                guardian_id=guardian_id,
                school_id=school_id,
                teacher_id=teacher_id,
                discount_code=None,
                discount=discount,
                sub_total=sub_total,
                total=total,
                payment_method=payment_method,
                order_detail_list=order_detail_input,
                return_url=return_url,
                card_number=card_number,
                card_exp_month=card_exp_month,
                card_exp_year=card_exp_year,
                card_cvc=card_cvc,
                card_first_name=card_first_name,
                card_last_name=card_last_name,
                address1=address1,
                address2=address2,
                city=city,
                state=state,
                post_code=post_code,
                country=country,
                phone=phone
            )
            print("after create services")

            PaymentHistory.objects.create(
                type="backend_anction_order_create",
                user=user,
                order=create_order_resp.order
            )
            return CreateOrder(
                guardian=create_order_resp.order.guardian,
                teacher=create_order_resp.order.teacher,
                school=create_order_resp.order.school,
                order=create_order_resp.order,
                status="success",
                url_redirect=create_order_resp.url_redirect
            )
        except (Exception, AssertionError, DatabaseError) as e:
            # transaction.rollback()
            try:
                PaymentHistory.objects.create(
                    type="backend_anction_order_create_error",
                    user=user,
                    message=str(e)
                )
            except Exception as err:
                print(err)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


# Confirm order have been paid
class ConfirmPaymentOrder(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
    teacher = graphene.Field('organization.schema.TeacherSchema')
    school = graphene.Field('organization.schema.SchoolSchema')
    order = graphene.Field('payments.schema.OrderSchema')
    status = graphene.String()

    class Arguments:
        order_id = graphene.ID(required=True)

    def mutate(
            self,
            info,
            order_id
    ):
        try:
            with transaction.atomic():

                order = services.confirm_order_payment(order_id)

                # plan_services.create_guardian_student_plan(order)
                if order.guardian is not None:
                    user = order.guardian.user
                elif order.teacher is not None:
                    user = order.teacher.user
                elif order.school is not None:
                    school = order.school
                    user = SchoolSubscriber.objects.get(
                        school=school).subscriber.user

                PaymentHistory.objects.create(
                    type="backend_anction_confirm_payment_order",
                    user=user,
                    order=order
                )
                return ConfirmPaymentOrder(
                    guardian=order.guardian,
                    teacher=order.teacher,
                    school=order.school,
                    order=order,
                    status="success"
                )
        except (Exception, DatabaseError) as e:
            transaction.rollback()
            print(str(e))
            try:
                order = Order.objects.get(pk=order_id)
                if order.guardian is not None:
                    user = order.guardian.user
                elif order.teacher is not None:
                    user = order.teacher.user
                elif order.school is not None:
                    school = order.school

                    user = SchoolSubscriber.objects.get(
                        school=school).subscriber.user
                PaymentHistory.objects.create(
                    type="backend_anction_confirm_payment_order_error",
                    user=user,
                    order=order,
                    message=str(e)
                )
            except Exception as err:
                return err
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


# Add new payment
class ChangePaymentMethod(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
    teacher = graphene.Field(TeacherSchema)
    school = graphene.Field(SchoolSchema)
    subscriber = graphene.Field(SubscriberSchema)
    status = graphene.String()

    class Arguments:
        school_id = graphene.ID(required=False)
        method = graphene.String(required=True)
        first_name = graphene.String(required=False)
        last_name = graphene.String(required=False)
        card_number = graphene.String(required=False)
        card_exp_month = graphene.String(required=False)
        card_exp_year = graphene.String(required=False)
        card_cvc = graphene.String(required=False)
        address1 = graphene.String(required=False)
        address2 = graphene.String(required=False)
        city = graphene.String(required=False)
        state = graphene.String(required=False)
        post_code = graphene.String(required=False)
        country = graphene.String(required=False)
        phone = graphene.String(required=False)

    def mutate(
            self,
            info,
            method,
            school_id=None,
            first_name=None,
            last_name=None,
            card_number=None,
            card_exp_month=None,
            card_exp_year=None,
            card_cvc=None,
            address1=None,
            address2=None,
            city=None,
            state=None,
            post_code=None,
            country=None,
            phone=None
    ):
        try:
            with transaction.atomic():
                user = info.context.user
                role = user.profile.role
                if user.is_anonymous:
                    raise Exception('Authentication Required')
                if (role != "teacher" and role != "subscriber" and role != "guardian"):
                    raise Exception("You don't have permission")
                subscriber = None
                guardian = None
                teacher = None
                if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "subscriber"):
                    subscriber = user.schoolpersonnel.subscriber
                    if (school_id is None):
                        raise Exception('Please send school id.')
                    if (SchoolSubscriber.objects.filter(school_id=school_id, subscriber=subscriber).count() < 1):
                        raise Exception('This school is not your school.')

                if hasattr(user, "guardian"):
                    guardian = user.guardian

                if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "teacher"):
                    teacher = user.schoolpersonnel.teacher
                    # raise Exception(f"unpaid for card in sub_id: {order_detail.subscription_id}")

                services.change_default_payment_method(
                    guardian_id=guardian.id if guardian is not None else None,
                    teacher_id=teacher.id if teacher is not None else None,
                    school_id=school_id,
                    method=method,
                    card_number=card_number,
                    card_exp_month=card_exp_month,
                    card_exp_year=card_exp_year,
                    card_cvc=card_cvc,
                    card_first_name=first_name,
                    card_last_name=last_name,
                    address1=address1,
                    address2=address2,
                    city=city,
                    state=state,
                    post_code=post_code,
                    country=country,
                    phone=phone
                )

                user = services.change_order_detail_payment_method(
                    guardian_id=guardian.id if guardian is not None else None,
                    teacher_id=teacher.id if teacher is not None else None,
                    school_id=school_id,
                )
                guardian = user.guardian
                PaymentHistory.objects.create(
                    type="backend_anction_change_default_payment_method",
                    user=user,
                    card_number=card_number
                )
                return ChangePaymentMethod(
                    guardian=guardian,
                    school=School.objects.get(
                        pk=school_id) if school_id is not None else None,
                    teacher=teacher,
                    subscriber=subscriber,
                    status="success"
                )
        except (Exception, DatabaseError) as e:
            transaction.rollback()
            try:
                PaymentHistory.objects.create(
                    type="backend_anction_change_default_payment_method_error",
                    user=user,
                    card_number=card_number,
                    message=str(e)
                )
            except Exception as err:
                return err
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


# Add new payment
class EditPaymentMethod(graphene.Mutation):
    payment_method = graphene.Field(PaymentMethodSchema)
    status = graphene.String()

    class Arguments:
        payment_method_id = graphene.ID(required=True)
        first_name = graphene.String(required=False)
        last_name = graphene.String(required=False)
        card_number = graphene.String(required=False)
        card_exp_month = graphene.String(required=False)
        card_exp_year = graphene.String(required=False)
        card_cvc = graphene.String(required=False)
        address1 = graphene.String(required=False)
        address2 = graphene.String(required=False)
        city = graphene.String(required=False)
        state = graphene.String(required=False)
        post_code = graphene.String(required=False)
        country = graphene.String(required=False)
        phone = graphene.String(required=False)

    def mutate(
            self,
            info,
            payment_method_id,
            first_name=None,
            last_name=None,
            card_number=None,
            card_exp_month=None,
            card_exp_year=None,
            card_cvc=None,
            address1=None,
            address2=None,
            city=None,
            state=None,
            post_code=None,
            country=None,
            phone=None
    ):
        try:
            with transaction.atomic():
                user = info.context.user
                role = user.profile.role
                if user.is_anonymous:
                    raise Exception('Authentication Required')
                if (role != "teacher" and role != "subscriber" and role != "guardian"):
                    raise Exception("You don't have permission")

                payment_method = services.edit_payment_method(
                    payment_method_id=payment_method_id,
                    card_number=card_number,
                    card_exp_month=card_exp_month,
                    card_exp_year=card_exp_year,
                    card_cvc=card_cvc,
                    card_first_name=first_name,
                    card_last_name=last_name,
                    address1=address1,
                    address2=address2,
                    city=city,
                    state=state,
                    post_code=post_code,
                    country=country,
                    phone=phone
                )
                user = services.change_order_detail_payment_method(
                    guardian_id=payment_method.guardian.id if payment_method.guardian else None,
                    teacher_id=payment_method.teacher.id if payment_method.teacher else None,
                    school_id=payment_method.school.id if payment_method.school else None,
                    payment_method_id=payment_method_id,
                )

                PaymentHistory.objects.create(
                    type="backend_anction_edit_payment_method",
                    user=user,
                    card_number=card_number
                )
                return EditPaymentMethod(
                    payment_method=payment_method,
                    status="success"
                )
        except (Exception, DatabaseError) as e:
            transaction.rollback()
            try:
                PaymentHistory.objects.create(
                    type="backend_anction_edit_payment_method_error",
                    user=user,
                    card_number=card_number,
                    message=str(e)
                )
            except Exception as err:
                return err
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


# Create new order with out pay
class CreateOrderWithOutPay(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
    order = graphene.Field('payments.schema.OrderSchema')
    status = graphene.String()
    teacher = graphene.Field('organization.schema.TeacherSchema')
    school = graphene.Field('organization.schema.SchoolSchema')

    class Arguments:
        guardian_id = graphene.ID(required=False)
        teacher_id = graphene.ID(required=False)
        school_id = graphene.ID(required=False)
        order_detail_input = graphene.List(OrderDetailInput)
        first_name = graphene.String(required=False)
        last_name = graphene.String(required=False)
        address1 = graphene.String(required=False)
        address2 = graphene.String(required=False)
        city = graphene.String(required=False)
        state = graphene.String(required=False)
        post_code = graphene.String(required=False)
        country = graphene.String(required=False)
        phone = graphene.String(required=False)

    def mutate(
            self,
            info,
            order_detail_input,
            guardian_id=None,
            teacher_id=None,
            school_id=None,
            first_name=None,
            last_name=None,
            address1=None,
            address2=None,
            city=None,
            state=None,
            post_code=None,
            country=None,
            phone=None
    ):
        if guardian_id is not None:
            user = User.objects.get(guardian__id=guardian_id)
        elif teacher_id is not None:
            user = User.objects.get(schoolpersonnel__teacher__id=teacher_id)
        elif school_id is not None:
            user = SchoolSubscriber.objects.get(
                school_id=school_id).subscriber.user
        try:
            with transaction.atomic():
                create_order_resp = services.create_order_with_out_pay(
                    guardian_id=guardian_id,
                    teacher_id=teacher_id,
                    school_id=school_id,
                    order_detail_list=order_detail_input,
                )
                services.confirm_order_payment(
                    create_order_resp.order.id,
                    first_name=first_name,
                    last_name=last_name,
                    address1=address1,
                    address2=address2,
                    city=city,
                    state=state,
                    post_code=post_code,
                    country=country,
                    phone=phone
                )
                PaymentHistory.objects.create(
                    type="backend_anction_create_order_without_pay",
                    user=user,
                    order=create_order_resp.order,
                )
                return CreateOrderWithOutPay(
                    guardian=create_order_resp.order.guardian,
                    teacher=create_order_resp.order.teacher,
                    school=create_order_resp.order.school,
                    order=create_order_resp.order,
                    status="success",
                )
        except (Exception, AssertionError, DatabaseError) as e:
            transaction.rollback()
            try:

                PaymentHistory.objects.create(
                    type="backend_anction_create_order_without_pay_error",
                    user=user,
                    message=str(e)
                )
            except Exception as err:
                print(err)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class CancelOrderdetailById(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
    student = graphene.Field(StudentSchema)
    subscriber = graphene.Field(SubscriberSchema)
    teacher = graphene.Field(TeacherSchema)
    administrativepersonnel = graphene.Field(AdministrativePersonnelSchema)
    status = graphene.String()

    class Arguments:
        order_detail_id = graphene.ID(required=True)
        reason = graphene.String(required=True)

    def mutate(
            self,
            info,
            order_detail_id,
            reason):
        try:
            with transaction.atomic():
                user = info.context.user
                if user.is_anonymous:
                    raise Exception('Authentication Required')
                order_detail = OrderDetail.objects.get(pk=order_detail_id)

                old_payment = order_detail.order.payment_method

                if old_payment == "CARD":
                    card = Card()
                    sub = card.cancel_subscription(
                        sub_id=order_detail.subscription_id)

                    if sub.status != "canceled":
                        raise Exception(
                            f"cannot unsub order_detail_id {order_detail.id} from stripe")

                order_detail.status = "canceled"
                order_detail.cancel_reason = reason
                order_detail.is_cancel = True
                order_detail.update_timestamp = timezone.now()
                order_detail.save()

                # cancel guardian student plan
                guardian_student_plans = GuardianStudentPlan.objects.filter(
                    order_detail_id=order_detail.id)
                for guardian_student_plan in guardian_student_plans:
                    guardian_student_plan.is_cancel = True
                    guardian_student_plan.cancel_reason = reason
                    guardian_student_plan.update_timestamp = timezone.now()
                    guardian_student_plan.save()

                teacher_classrooms = TeacherClassroom.objects.filter(
                    order_detail_id=order_detail.id)
                for teacher_classroom in teacher_classrooms:
                    teacher_classroom.is_cancel = True
                    teacher_classroom.cancel_reason = reason
                    teacher_classroom.update_timestamp = timezone.now()
                    teacher_classroom.save()

                school_teachers = SchoolTeacher.objects.filter(
                    order_detail_id=order_detail.id)
                for school_teacher in school_teachers:
                    school_teacher.is_cancel = True
                    school_teacher.cancel_reason = reason
                    school_teacher.update_timestamp = timezone.now()
                    school_teacher.save()

                guardian = user.guardian if hasattr(user, "guardian") else None
                student = user.student if hasattr(user, "student") else None
                subscriber = user.schoolpersonnel.subscriber if hasattr(
                    user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "subscriber") else None
                teacher = user.schoolpersonnel.teacher if hasattr(
                    user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "teacher") else None
                administrativepersonnel = user.schoolpersonnel.administrativepersonnel if hasattr(
                    user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "administrativepersonnel") else None

                return CancelOrderdetailById(
                    guardian=guardian,
                    student=student,
                    subscriber=subscriber,
                    teacher=teacher,
                    administrativepersonnel=administrativepersonnel,
                    status="success"
                )
        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class TmpOrderDetailInput:
    plan_id: int
    quantity: int
    period: str

    def __init__(self, plan_id, quantity, period):
        self.plan_id = plan_id
        self.quantity = quantity
        self.period = period


class UpdateOrderdetailById(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
    student = graphene.Field(StudentSchema)
    subscriber = graphene.Field(SubscriberSchema)
    teacher = graphene.Field(TeacherSchema)
    order = graphene.Field('payments.schema.OrderSchema')
    url_redirect = graphene.String()
    status = graphene.String()

    class Arguments:
        order_detail_id = graphene.ID(required=True)
        period = graphene.String()
        return_url = graphene.String(required=True)
        school_id = graphene.ID(required=False)

    def mutate(
            self,
            info,
            order_detail_id,
            period,
            return_url,
            school_id=None,
    ):
        try:
            with transaction.atomic():
                user = info.context.user
                role = user.profile.role
                if user.is_anonymous:
                    raise Exception('Authentication Required')
                if (role != "teacher" and role != "subscriber" and role != "guardian"):
                    raise Exception("You don't have permission")

                if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "subscriber"):
                    subscriber = user.schoolpersonnel.subscriber
                    if (school_id is None):
                        raise Exception('Please send school id.')
                    if (SchoolSubscriber.objects.filter(school_id=school_id, subscriber=subscriber).count() < 1):
                        raise Exception('This school is not your school.')

                if hasattr(user, "guardian"):
                    guardian = user.guardian
                    if (OrderDetail.objects.filter(pk=order_detail_id, order__guardian=guardian).count() < 1):
                        raise Exception(
                            "You don't have permission to change this order detail!")

                if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "teacher"):
                    teacher = user.schoolpersonnel.teacher.id
                    if (OrderDetail.objects.filter(pk=order_detail_id, order__teacher=teacher).count() < 1):
                        raise Exception(
                            "You don't have permission to change this order detail!")

                order_detail = OrderDetail.objects.get(pk=order_detail_id)

                if order_detail.is_cancel:
                    raise Exception(
                        f"order detail id {order_detail.id} already cancel")

                order_detail_input = [TmpOrderDetailInput(
                    plan_id=order_detail.plan.id,
                    quantity=order_detail.quantity,
                    period=period
                )]

                payment_method = PaymentMethod.objects.get(
                    guardian_id=user.guardian.id if hasattr(
                        user, "guardian") else None,
                    teacher_id=user.schoolpersonnel.teacher.id if hasattr(
                        user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "teacher") else None,
                    school_id=school_id,
                    is_default=True
                )

                # create new subscribe
                order_resp = payment_services.create_order(
                    guardian_id=user.guardian.id if hasattr(
                        user, "guardian") else None,
                    teacher_id=user.schoolpersonnel.teacher.id if hasattr(
                        user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "teacher") else None,
                    school_id=school_id,
                    discount_code="",
                    discount=0,
                    sub_total=0,
                    total=0,
                    payment_method=payment_method.method,
                    order_detail_list=order_detail_input,
                    return_url=return_url,
                    card_first_name=payment_method.card_first_name,
                    card_last_name=payment_method.card_last_name,
                    card_number=payment_method.card_number,
                    card_exp_month=payment_method.card_exp_month,
                    card_exp_year=payment_method.card_exp_year,
                    card_cvc=payment_method.card_cvc,
                    address1=payment_method.address1,
                    address2=payment_method.address2,
                    city=payment_method.city,
                    state=payment_method.state,
                    post_code=payment_method.post_code,
                    country=payment_method.country,
                    phone=payment_method.phone,
                    order_detail_id=order_detail.id
                )

                return UpdateOrderdetailById(
                    student=user.student if hasattr(user, "student") else None,
                    guardian=user.guardian if hasattr(
                        user, "guardian") else None,
                    subscriber=user.schoolpersonnel.subscriber if hasattr(
                        user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "subscriber") else None,
                    teacher=user.schoolpersonnel.teacher if hasattr(
                        user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "teacher") else None,
                    order=order_resp.order,
                    url_redirect=order_resp.url_redirect,
                    status="success"
                )
        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class ConfirmUpdateOrderdetail(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
    subscriber = graphene.Field(SubscriberSchema)
    teacher = graphene.Field(TeacherSchema)
    order = graphene.Field('payments.schema.OrderSchema')
    status = graphene.String()

    class Arguments:
        order_detail_id = graphene.ID(required=True)
        school_id = graphene.ID(required=False)

    def mutate(
            self,
            info,
            order_detail_id,
            school_id=None,
    ):
        try:
            with transaction.atomic():
                user = info.context.user
                role = user.profile.role
                if user.is_anonymous:
                    raise Exception('Authentication Required')
                if (role != "teacher" and role != "subscriber" and role != "guardian"):
                    raise Exception("You don't have permission")
                subscriber = None
                guardian = None
                teacher = None
                if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "subscriber"):
                    subscriber = user.schoolpersonnel.subscriber
                    if (school_id is None):
                        raise Exception('Please send school id.')
                    if (SchoolSubscriber.objects.filter(school_id=school_id, subscriber=subscriber).count() < 1):
                        raise Exception('This school is not your school.')

                if hasattr(user, "guardian"):
                    guardian = user.guardian
                    if (OrderDetail.objects.filter(pk=order_detail_id, order__guardian=guardian).count() < 1):
                        raise Exception(
                            "You don't have permission to change this order detail!")

                if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "teacher"):
                    teacher = user.schoolpersonnel.teacher
                    if (OrderDetail.objects.filter(pk=order_detail_id, order__teacher=teacher).count() < 1):
                        raise Exception(
                            "You don't have permission to change this order detail!")
                    # raise Exception(f"unpaid for card in sub_id: {order_detail.subscription_id}")
                new_order_detail = OrderDetail.objects.get(pk=order_detail_id)
                old_order_detail = OrderDetail.objects.get(
                    pk=new_order_detail.update_from_detail_id)
                card = Card()
                result_sub = card.check_subscription(
                    new_order_detail.subscription_id)
                all_paid = True
                if result_sub["status"] != "active" and result_sub["status"] != "trialing":
                    all_paid = False
                period = 2
                new_order_detail.status = result_sub["status"]
                new_order_detail.expired_at = result_sub["expired_at"] + datetime.timedelta(
                    days=period)
                new_order_detail.is_paid = all_paid
                new_order_detail.save()

                order = new_order_detail.order
                # add new order_detail to guardian student plan

                guardian_student_plans = GuardianStudentPlan.objects.filter(
                    order_detail_id=old_order_detail.id)
                for guardian_student_plan in guardian_student_plans:
                    guardian_student_plan.order_detail_id = new_order_detail.id
                    guardian_student_plan.is_paid = new_order_detail.is_paid
                    guardian_student_plan.is_cancel = new_order_detail.is_cancel
                    guardian_student_plan.expired_at = new_order_detail.expired_at
                    guardian_student_plan.period = new_order_detail.period
                    guardian_student_plan.price = new_order_detail.total

                    guardian_student_plan.save()

                teacher_classrooms = TeacherClassroom.objects.filter(
                    order_detail_id=old_order_detail.id)
                for teacher_classroom in teacher_classrooms:
                    teacher_classroom.order_detail_id = new_order_detail.id
                    teacher_classroom.is_paid = new_order_detail.is_paid
                    teacher_classroom.is_cancel = new_order_detail.is_cancel
                    teacher_classroom.expired_at = new_order_detail.expired_at
                    teacher_classroom.period = new_order_detail.period
                    teacher_classroom.price = new_order_detail.total

                    teacher_classroom.save()

                school_teachers = SchoolTeacher.objects.filter(
                    order_detail_id=old_order_detail.id)
                for school_teacher in school_teachers:
                    school_teacher.order_detail_id = new_order_detail.id
                    school_teacher.is_paid = new_order_detail.is_paid
                    school_teacher.is_cancel = new_order_detail.is_cancel
                    school_teacher.expired_at = new_order_detail.expired_at
                    school_teacher.period = new_order_detail.period
                    school_teacher.price = new_order_detail.total

                    school_teacher.save()

                # cancel old order_detail
                old_payment = old_order_detail.order.payment_method

                if old_payment == "CARD":
                    card = Card()
                    sub = card.cancel_subscription(
                        sub_id=old_order_detail.subscription_id)

                    if sub.status != "canceled":
                        raise Exception(
                            f"cannot unsub order_detail_id {old_order_detail.id} from stripe")

                old_order_detail.is_cancel = True
                old_order_detail.cancel_reason = "Update subscription period."
                old_order_detail.update_timestamp = timezone.now()
                old_order_detail.save()
                return ConfirmUpdateOrderdetail(
                    guardian=guardian,
                    subscriber=subscriber,
                    teacher=teacher,
                    order=order,
                    status="success"
                )
        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class AddOrder(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
    teacher = graphene.Field('organization.schema.TeacherSchema')
    subscriber = graphene.Field(SubscriberSchema)
    school = graphene.Field('organization.schema.SchoolSchema')
    order = graphene.Field('payments.schema.OrderSchema')
    order = graphene.Field('payments.schema.OrderSchema')
    url_redirect = graphene.String()
    status = graphene.String()

    class Arguments:
        school_id = graphene.ID(required=False)
        order_detail_input = graphene.List(OrderDetailInput)
        return_url = graphene.String(required=True)
        coupon = graphene.String(required=False)

    def mutate(
            self,
            info,
            order_detail_input,
            return_url,
            coupon=None,
            school_id=None
    ):
        try:
            # with transaction.atomic():
            user = info.context.user
            role = user.profile.role
            if user.is_anonymous:
                raise Exception('Authentication Required')
            if (role != "teacher" and role != "subscriber" and role != "guardian"):
                raise Exception("You don't have permission")
            subscriber = None
            guardian = None
            teacher = None
            school = None
            if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "subscriber"):
                subscriber = user.schoolpersonnel.subscriber
                if (school_id is None):
                    raise Exception('Please send school id.')
                if (SchoolSubscriber.objects.filter(school_id=school_id, subscriber=subscriber).count() < 1):
                    raise Exception('This school is not your school.')
                school = School.objects.get(pk=school_id)

            if hasattr(user, "guardian"):
                guardian = user.guardian

            if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "teacher"):
                teacher = user.schoolpersonnel.teacher

            payment_method = PaymentMethod.objects.get(
                teacher=teacher,
                school=school,
                guardian=guardian,
                is_default=True
            )

            order_resp = payment_services.create_order(
                guardian_id=guardian.id if guardian is not None else None,
                school_id=school.id if school is not None else None,
                teacher_id=teacher.id if teacher is not None else None,
                discount_code=coupon,
                discount=0,
                sub_total=0,
                total=0,
                payment_method=payment_method.method,
                order_detail_list=order_detail_input,
                return_url=return_url,
                card_first_name=payment_method.card_first_name,
                card_last_name=payment_method.card_last_name,
                card_number=payment_method.card_number,
                card_exp_month=payment_method.card_exp_month,
                card_exp_year=payment_method.card_exp_year,
                card_cvc=payment_method.card_cvc,
                address1=payment_method.address1,
                address2=payment_method.address2,
                city=payment_method.city,
                state=payment_method.state,
                post_code=payment_method.post_code,
                country=payment_method.country,
                phone=payment_method.phone
            )

            return AddOrder(
                guardian=guardian,
                teacher=teacher,
                subscriber=subscriber,
                school=school,
                order=order_resp.order,
                url_redirect=order_resp.url_redirect,
                status="success"
            )
        except (Exception, DatabaseError) as e:
            # transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e

# Cancel membership (all order_detail and guardian student plan)


class CancelMembership(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
    student = graphene.Field(StudentSchema)
    subscriber = graphene.Field(SubscriberSchema)
    teacher = graphene.Field(TeacherSchema)
    administrativepersonnel = graphene.Field(AdministrativePersonnelSchema)
    status = graphene.String()

    class Arguments:
        reason = graphene.String(required=True)

    def mutate(
            self,
            info,
            reason):
        try:
            with transaction.atomic():
                user = info.context.user
                role = user.profile.role
                if user.is_anonymous:
                    raise Exception('Authentication Required')
                if (role != "teacher" and role != "subscriber" and role != "guardian"):
                    raise Exception("You don't have permission")

                guardian = None
                teacher = None
                subscriber = None
                schools = []

                if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "subscriber"):
                    subscriber = user.schoolpersonnel.subscriber

                if hasattr(user, "guardian"):
                    guardian = user.guardian

                if hasattr(user, "schoolpersonnel") and hasattr(user.schoolpersonnel, "teacher"):
                    teacher = user.schoolpersonnel.teacher

                if (guardian):
                    guardian_student_plans = guardian.guardianstudentplan_set.all()
                    for guardian_student_plan in guardian_student_plans:
                        guardian_student_plan.is_cancel = True
                        guardian_student_plan.cancel_reason = reason
                        guardian_student_plan.update_timestamp = timezone.now()
                        guardian_student_plan.save()
                elif (teacher):
                    # print(teacher)
                    teacher_classrooms = teacher.teacherclassroom_set.all()
                    for teacher_classroom in teacher_classrooms:
                        teacher_classroom.is_cancel = True
                        teacher_classroom.cancel_reason = reason
                        teacher_classroom.update_timestamp = timezone.now()
                        teacher_classroom.save()
                else:
                    school_subscribers = subscriber.schoolsubscriber_set.all()
                    for school_subscriber in school_subscribers:
                        school = school_subscriber.school
                        schools.append(school)
                        school_teachers = school.schoolteacher_set.all()
                        for school_teacher in school_teachers:
                            school_teacher.is_cancel = True
                            school_teacher.cancel_reason = reason
                            school_teacher.update_timestamp = timezone.now()
                            school_teacher.save()
                if len(schools) > 0:
                    order_details = OrderDetail.objects.filter(
                        order__school__in=schools, is_cancel=False)
                else:
                    order_details = OrderDetail.objects.filter(
                        order__guardian=guardian, order__teacher=teacher, is_cancel=False)
                print("order details : ", order_details)
                for order_detail in order_details:
                    if order_detail.order.payment_method == "CARD":
                        card = Card()

                        try:
                            sub = card.cancel_subscription(
                                order_detail.subscription_id)
                            if sub.status != "canceled":
                                raise Exception(
                                    f"cannot unsub order_detail_id {order_detail.id} from stripe")
                        except (Exception, AssertionError, DatabaseError) as e:
                            print(e)

                    order_detail.status = "canceled"
                    order_detail.cancel_reason = reason
                    order_detail.is_cancel = True
                    order_detail.update_timestamp = timezone.now()
                    order_detail.save()

                return CancelMembership(
                    guardian=guardian,
                    teacher=teacher,
                    subscriber=subscriber,
                    status="success"
                )
        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


class Mutation(graphene.ObjectType):
    create_order = CreateOrder.Field()
    create_order_with_out_pay = CreateOrderWithOutPay.Field()
    confirm_payment_order = ConfirmPaymentOrder.Field()
    change_payment_method = ChangePaymentMethod.Field()
    edit_payment_method = EditPaymentMethod.Field()
    cancel_orderdetail_by_id = CancelOrderdetailById.Field()
    update_orderdetail_by_id = UpdateOrderdetailById.Field()
    confirm_update_orderdetail = ConfirmUpdateOrderdetail.Field()
    cancel_membership = CancelMembership.Field()
    add_order = AddOrder.Field()
