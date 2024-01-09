import calendar
import datetime
import os
import sys
from decimal import Decimal

import graphene
from django.db import transaction, DatabaseError
from django.utils import timezone
from graphene import ID
from organization.schema import AdministrativePersonnelSchema, SubscriberSchema, TeacherSchema

from payments.card import Card
from payments.models import PaymentMethod, Order, OrderDetail
from students.models import Student
from students.schema import StudentSchema
from .models import Plan, GuardianStudentPlan
from guardians.models import Guardian
from kb.models import AreaOfKnowledge
from app.utils import add_months
import payments.services as payment_services
from payments.mutations import OrderDetailInput


class TmpOrderDetailInput:
    plan_id: int
    quantity: int
    period: str

    def __init__(self, plan_id, quantity, period):
        self.plan_id = plan_id
        self.quantity = quantity
        self.period = period


class AddGuardianPlan(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
    order = graphene.Field('payments.schema.OrderSchema')
    url_redirect = graphene.String()
    status = graphene.String()

    class Arguments:
        guardian_id = graphene.ID(required=True)
        order_detail_input = graphene.List(OrderDetailInput)
        return_url = graphene.String(required=True)
        coupon = graphene.String(required=False)

    def mutate(
            self,
            info,
            guardian_id,
            order_detail_input,
            return_url,
            coupon=None
    ):
        try:
            # with transaction.atomic():

                payment_method = PaymentMethod.objects.get(guardian_id=guardian_id, is_default=True)

                order_resp = payment_services.create_order(
                    guardian_id=guardian_id,
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

                return AddGuardianPlan(
                    guardian=order_resp.order.guardian,
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


class UpdateGuardianPlan(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
    order = graphene.Field('payments.schema.OrderSchema')
    url_redirect = graphene.String()
    status = graphene.String()

    class Arguments:
        order_detail_id = graphene.ID(required=True)
        guardian_id = graphene.ID(required=True)
        period = graphene.String()
        return_url = graphene.String(required=True)

    def mutate(
            self,
            info,
            order_detail_id,
            guardian_id,
            period,
            return_url
    ):
        try:
            with transaction.atomic():

                order_detail = OrderDetail.objects.get(pk=order_detail_id)

                if order_detail.is_cancel:
                    raise Exception(f"order detail id {order_detail.id} already cancel")

                order_detail_input = [TmpOrderDetailInput(
                    plan_id=order_detail.plan.id,
                    quantity=order_detail.quantity,
                    period=period
                )]

                payment_method = PaymentMethod.objects.get(guardian_id=guardian_id, is_default=True)

                # create new subscribe
                order_resp = payment_services.create_order(
                    guardian_id=guardian_id,
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

                return UpdateGuardianPlan(
                    guardian=order_resp.order.guardian,
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


# Confirm update have been paid
class ConfirmUpdateGuardianPlan(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
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

                order = payment_services.confirm_order_payment(order_id)

                new_order_detail = OrderDetail.objects.get(order_id=order.id)
                old_order_detail = OrderDetail.objects.get(pk=new_order_detail.update_from_detail_id)

                # add new order_detail to guardian student plan
                guardian_student_plans = GuardianStudentPlan.objects.filter(order_detail_id=old_order_detail.id)

                for guardian_student_plan in guardian_student_plans:
                    guardian_student_plan.order_detail_id = new_order_detail.id
                    guardian_student_plan.is_paid = new_order_detail.is_paid
                    guardian_student_plan.is_cancel = new_order_detail.is_cancel
                    guardian_student_plan.expired_at = new_order_detail.expired_at
                    guardian_student_plan.period = new_order_detail.period
                    guardian_student_plan.price = new_order_detail.total

                    guardian_student_plan.save()


                # cancel old order_detail
                old_payment = old_order_detail.order.payment_method

                if old_payment == "CARD":
                    card = Card()
                    sub = card.cancel_subscription(sub_id=old_order_detail.subscription_id)

                    if sub.status != "canceled":
                        raise Exception(f"cannot unsub order_detail_id {old_order_detail.id} from stripe")

                old_order_detail.is_cancel = True
                old_order_detail.update_timestamp = timezone.now()
                old_order_detail.save()

                return ConfirmUpdateGuardianPlan(
                    guardian=order.guardian,
                    order=order,
                    status="success"
                )
        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e


# check guardian plan
class CheckGuardianPlan(graphene.Mutation):
    guardian = graphene.Field('guardians.schema.GuardianSchema')
    order_detail = graphene.Field('payments.schema.OrderDetailSchema')

    class Arguments:
        order_detail_id = graphene.ID(required=True)

    def mutate(
            self,
            info,
            order_detail_id):
        try:
            with transaction.atomic():
                order_detail = payment_services.check_order_detail(order_detail_id=order_detail_id)

                return CheckGuardianPlan(
                    guardian=order_detail.order.guardian,
                    order_detail=order_detail
                )
        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e
# # Create new GuardianStudentPlan
# class CreateGuardianStudentPlan(graphene.Mutation):
#     guardian_student_plan = graphene.Field('plans.schema.GuardianStudentPlanSchema')
#     order = graphene.Field('payments.schema.OrderSchema')
#     url_redirect = graphene.String()
#
#     class Arguments:
#         guardian_id = graphene.ID(required=True)
#         plan_id = graphene.ID(required=True)
#         list_subject_id = graphene.List(ID)
#         period = graphene.String(required=True)
#         price = graphene.Decimal(required=True)
#         student_id = graphene.ID(required=False)
#         return_url = graphene.String(required=True)
#
#     def mutate(
#             self,
#             info,
#             guardian_id,
#             plan_id,
#             list_subject_id,
#             period,
#             price,
#             return_url,
#             student_id=None
#     ):
#         try:
#             with transaction.atomic():
#                 guardian = Guardian.objects.get(pk=guardian_id)
#                 plan = Plan.objects.get(pk=plan_id)
#
#                 if period != "Monthly" and period != "Yearly":
#                     raise Exception("period must be Monthly or Yearly.")
#
#                 guardian_student_plan = GuardianStudentPlan.objects.create(
#                     guardian_id=guardian.id,
#                     plan_id=plan.id,
#                     period=period,
#                     price=price,
#                     is_paid=False
#                 )
#
#                 guardian_student_plan.save()
#
#                 # list of subject
#                 if guardian_student_plan.plan.area_of_knowledge == "ALL":
#                     subjects = AreaOfKnowledge.objects.all()
#                     for subject in subjects:
#                         guardian_student_plan.subject.add(subject)
#                 elif len(list_subject_id) != 0:
#                     for subject_id in list_subject_id:
#                         subject = AreaOfKnowledge.objects.get(pk=subject_id)
#                         guardian_student_plan.subject.add(subject)
#
#                 if student_id:
#                     student = Student.objects.get(pk=student_id)
#                     guardian_student_plan.student_id = student.id
#
#                 guardian_student_plan.save()
#
#                 payment_method = PaymentMethod.objects.get(guardian_id=guardian_student_plan.guardian.id,
#                                                            is_default=True)
#                 order_detail_input = OrderDetailInput(
#                     plan_id=guardian_student_plan.plan_id,
#                     quantity=1,
#                     total=price,
#                     period=period,
#                     guardian_student_plan_id=guardian_student_plan.id
#                 )
#                 create_order_resp = payment_services.create_order(
#                     guardian_id=guardian_student_plan.guardian.id,
#                     discount=0,
#                     discount_code="",
#                     sub_total=price,
#                     total=price,
#                     payment_method=payment_method.method,
#                     return_url=return_url,
#                     order_detail_input=[order_detail_input]
#                 )
#
#                 return CreateGuardianStudentPlan(
#                     guardian_student_plan=guardian_student_plan,
#                     order=create_order_resp.order,
#                     url_redirect=create_order_resp.url_redirect
#                 )
#         except (Exception, DatabaseError) as e:
#             transaction.rollback()
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#             print(exc_type, fname, exc_tb.tb_lineno)
#             return e


# # Update plan from yearly to monthly or another way around
# class UpdateGuardianStudentPlan(graphene.Mutation):
#     guardian_student_plan = graphene.Field('plans.schema.GuardianStudentPlanSchema')
#     order = graphene.Field('payments.schema.OrderSchema')
#     url_redirect = graphene.String()
#
#     class Arguments:
#         guardian_student_plan_id = graphene.ID(required=True)
#         period = graphene.String(required=True)
#         price = graphene.Decimal(required=True)
#         return_url = graphene.String(required=True)
#
#     def mutate(
#             self,
#             info,
#             guardian_student_plan_id,
#             period,
#             price,
#             return_url
#     ):
#         try:
#             with transaction.atomic():
#                 guardian_student_plan = GuardianStudentPlan.objects.get(pk=guardian_student_plan_id)
#
#                 if period != "Monthly" and period != "Yearly":
#                     raise Exception("period must be Monthly or Yearly.")
#                 #
#                 # guardian_student_plan.period = period
#                 # guardian_student_plan.price = price
#                 #
#                 # if period == "Monthly":
#                 #     expired_date = add_months(datetime.datetime.now(), 1)
#                 # else:
#                 #     expired_date = add_months(datetime.datetime.now(), 12)
#                 #
#                 # guardian_student_plan.expired_at = expired_date
#                 # guardian_student_plan.is_paid = True
#                 #
#                 # guardian_student_plan.save()
#                 payment_method = PaymentMethod.objects.get(guardian_id=guardian_student_plan.guardian.id, is_default=True)
#                 order_detail_input = OrderDetailInput(
#                     plan_id=guardian_student_plan.plan_id,
#                     quantity=1,
#                     total=price,
#                     period=period,
#                     guardian_student_plan_id=guardian_student_plan.id
#                 )
#                 create_order_resp = payment_services.create_order(
#                     guardian_id=guardian_student_plan.guardian.id,
#                     discount=0,
#                     discount_code="",
#                     sub_total=price,
#                     total=price,
#                     payment_method=payment_method.method,
#                     return_url=return_url,
#                     order_detail_input=[order_detail_input]
#                 )
#
#                 return UpdateGuardianStudentPlan(
#                     guardian_student_plan=guardian_student_plan,
#                     order=create_order_resp.order,
#                     url_redirect=create_order_resp.url_redirect
#                 )
#
#         except (Exception, DatabaseError) as e:
#             transaction.rollback()
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#             print(exc_type, fname, exc_tb.tb_lineno)
#             return e


# # Cancel plan with reason
# class CancelGuardianStudentPlan(graphene.Mutation):
#     guardian_student_plan = graphene.Field('plans.schema.GuardianStudentPlanSchema')
#
#     class Arguments:
#         guardian_student_plan_id = graphene.ID(required=True)
#         reason = graphene.String(required=True)
#
#     def mutate(
#             self,
#             info,
#             guardian_student_plan_id,
#             reason):
#         try:
#             with transaction.atomic():
#                 guardian_student_plan = GuardianStudentPlan.objects.get(pk=guardian_student_plan_id)
#                 guardian_student_plan.cancel_reason = reason
#                 guardian_student_plan.is_cancel = True
#                 guardian_student_plan.update_timestamp = timezone.now()
#                 guardian_student_plan.save()
#
#                 return CancelGuardianStudentPlan(
#                     guardian_student_plan=guardian_student_plan
#                 )
#         except (Exception, DatabaseError) as e:
#             transaction.rollback()
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#             print(exc_type, fname, exc_tb.tb_lineno)
#             return e
#
#
# # Cancel all the membership
# class CancelMembership(graphene.Mutation):
#     status = graphene.String()
#
#     class Arguments:
#         guardian_id = graphene.ID(required=True)
#         reason = graphene.String(required=True)
#
#     def mutate(
#             self,
#             info,
#             guardian_id,
#             reason):
#         try:
#             with transaction.atomic():
#                 guardian = Guardian.objects.get(pk=guardian_id)
#                 guardian_student_plans = GuardianStudentPlan.objects.filter(guardian_id=guardian.id)
#                 for guardian_student_plan in guardian_student_plans:
#                     guardian_student_plan.is_cancel = True
#                     guardian_student_plan.cancel_reason = reason
#                     guardian_student_plan.update_timestamp = timezone.now()
#                     guardian_student_plan.save()
#
#                 return CancelMembership(
#                     status="success"
#                 )
#         except (Exception, DatabaseError) as e:
#             transaction.rollback()
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#             print(exc_type, fname, exc_tb.tb_lineno)
#             return e


class Mutation(graphene.ObjectType):
    add_guardian_plan = AddGuardianPlan.Field()
    update_guardian_plan = UpdateGuardianPlan.Field()
    confirm_update_guardian_plan = ConfirmUpdateGuardianPlan.Field()
    check_guardian_plan = CheckGuardianPlan.Field()
