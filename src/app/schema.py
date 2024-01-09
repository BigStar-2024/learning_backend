import graphene
import graphql_jwt
from graphql_jwt import ObtainJSONWebToken

import achievements.schema
import api.schema
import audiences.schema
import block.schema
import block.mutations
import collectibles.schema
import collectibles.mutations
import emails.schema
import experiences.schema
import guardians.schema
import kb.schema
import organization.schema
import organization.mutations
import plans.schema
import students.schema
import students.mutations
import universals.schema
import users.schema
import wallets.schema
import avatars.schema
import avatars.mutations
import bank.mutations
import bank.schema
import plans.mutations
import payments.mutations
import payments.schema
import games.mutations
import games.schema
import users.mutations
import treasuretrack.schema
import treasuretrack.mutations
import badges.schema
import notes.schema
import notes.mutations
import certificates.schema
import certificates.mutations
from django.utils import timezone
import threading


class CustomTokenAuth(ObtainJSONWebToken):

    @classmethod
    def resolve(cls, root, info, **kwargs):
        print("========================")
        user = info.context.user
        role = user.profile.role
        if role == 'guardian':
            pass
        if role == 'student':
            student = user.student

            if hasattr(student, 'guardianstudentplan'):
                student_plan = student.guardianstudentplan
                # student_plan.is_cancel = student_plan.order_detail.is_cancel
                # student_plan.is_paid = student_plan.order_detail.is_paid
                # student_plan.expired_at = student_plan.order_detail.expired_at
                # student_plan.save()

                if student_plan.is_cancel:
                    raise Exception("Please reactive your plan")
                if student_plan.expired_at and student_plan.expired_at < timezone.now():
                    raise Exception("Expiration date has expired")

            elif hasattr(student, 'classroom'):
                teacher_classroom = student.classroom.teacherclassroom
                teacher = teacher_classroom.teacher
                school_teacher = teacher.schoolteacher if hasattr(
                    teacher, 'schoolteacher') else None
                school_teacher_is_cancel = False
                school_teacher_is_expired = False
                school_teacher_not_registered = False
                teacher_classroom_is_cancel = False
                teacher_classroom_is_expired = False

                if school_teacher:
                    if school_teacher.is_cancel:
                        school_teacher_is_cancel = True
                    if school_teacher.expired_at and school_teacher.expired_at < timezone.now():
                        school_teacher_is_expired = True
                else:
                    school_teacher_is_cancel = True
                    school_teacher_is_expired = True
                    school_teacher_not_registered = True

                if teacher_classroom.is_cancel:
                    teacher_classroom_is_cancel = True
                if teacher_classroom.expired_at and teacher_classroom.expired_at < timezone.now():
                    teacher_classroom_is_expired = True

                if ((school_teacher_is_cancel and not school_teacher_not_registered) or teacher_classroom_is_cancel):
                    raise Exception("Please reactive your plan")

                if ((school_teacher_is_expired and not school_teacher_not_registered) or teacher_classroom_is_cancel):
                    raise Exception("Expiration date has expired")

            else:
                raise Exception("You don't have any plan!")

            th = threading.Thread(target=student.import_new_topic)
            print("thread start")
            th.start()
        if role == 'subscriber':
            pass
        if role == 'teacher':
            pass
        if role == 'adminTeacher':
            pass

        # if hasattr(user, 'student'):
        #     student_plan = user.student.guardianstudentplan
        #     student_plan.is_cancel = student_plan.order_detail.is_cancel
        #     student_plan.is_paid = student_plan.order_detail.is_paid
        #     student_plan.expired_at = student_plan.order_detail.expired_at
        #     student_plan.save()

        #     if student_plan.is_cancel:
        #         raise Exception("Please reactive your plan")
        #     if student_plan.expired_at and student_plan.expired_at < timezone.now():
        #         raise Exception("Expiration date has expired")

        user.last_login = timezone.now()
        user.save()

        return cls()


class Mutation(
    api.schema.Mutation,
    block.mutations.Mutation,
    bank.mutations.Mutation,
    students.mutations.Mutation,
    collectibles.mutations.Mutation,
    emails.schema.Mutation,
    avatars.mutations.Mutation,
    plans.mutations.Mutation,
    payments.mutations.Mutation,
    games.mutations.Mutation,
    users.mutations.Mutation,
    treasuretrack.mutations.Mutation,
    organization.mutations.Mutation,
    certificates.mutations.Mutation,
    notes.mutations.Mutation,
    graphene.ObjectType
):
    token_auth = CustomTokenAuth.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    verify_token = graphql_jwt.Verify.Field()


class Query(
    avatars.schema.Query,
    achievements.schema.Query,
    api.schema.Query,
    audiences.schema.Query,
    block.schema.Query,
    bank.schema.Query,
    collectibles.schema.Query,
    experiences.schema.Query,
    games.schema.Query,
    guardians.schema.Query,
    kb.schema.Query,
    organization.schema.Query,
    payments.schema.Query,
    plans.schema.Query,
    students.schema.Query,
    treasuretrack.schema.Query,
    users.schema.Query,
    universals.schema.Query,
    wallets.schema.Query,
    badges.schema.Query,
    notes.schema.Query,
    certificates.schema.Query,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
