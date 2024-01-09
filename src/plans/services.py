from app.utils import add_months
from payments.models import Order, OrderDetail
from .models import GuardianStudentPlan


def create_guardian_student_plan(order: Order):
    # create GuardianStudentPlan if payment is complete
    order_details = OrderDetail.objects.filter(order_id=order.id)
    for order_detail in order_details:
        # create GuardianStudentPlan
        for package_amount in range(0, order_detail.quantity):
            guardian_student_plan = GuardianStudentPlan.objects.create(
                order_detail_id=order_detail.id,
                guardian_id=order.guardian.id,
                plan_id=order_detail.plan.id,
            )
            guardian_student_plan.save()
