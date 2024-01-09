import graphene
from graphene_django import DjangoObjectType
from plans.models import StudentPlan, Plan, GuardianStudentPlan
from kb.models import AreaOfKnowledge
from kb.schema import AreaOfKnowledgeSchema


class PlanSchema(DjangoObjectType):
    class Meta:
        model = Plan
        fields = "__all__"

    subjects = graphene.List(AreaOfKnowledgeSchema)

    def resolve_subjects(self, info):
        return AreaOfKnowledge.objects.filter(is_active=True)


class GuardianStudentPlanSchema(DjangoObjectType):
    subject = graphene.List(AreaOfKnowledgeSchema)

    def resolve_subject(self, info):
        subject = self.subject.filter(
            # audience=self.student.audience,
            is_active=True
        )
        return subject

    class Meta:
        model = GuardianStudentPlan
        fields = "__all__"


class StudentPlanSchema(DjangoObjectType):
    class Meta:
        model = StudentPlan
        fields = "__all__"


class Query(graphene.ObjectType):
    # ----------------- Plan ----------------- #
    plans = graphene.List(PlanSchema)
    plan_by_id = graphene.Field(PlanSchema, id=graphene.String())

    def resolve_plans(self, info, **kwargs):
        # Querying a list
        return Plan.objects.all()

    def resolve_plan_by_id(self, info, id):
        # Querying a single question
        return Plan.objects.get(pk=id)

    # ----------------- Guardian Plan ----------------- #
    guardian_student_plans = graphene.List(GuardianStudentPlanSchema)
    guardian_student_plan_by_guardian_id = graphene.List(GuardianStudentPlanSchema, guardian_id=graphene.String())
    guardian_student_plan_by_id = graphene.Field(GuardianStudentPlanSchema, id=graphene.String())

    def resolve_guardian_student_plans(self, info, **kwargs):
        # Querying a list
        return GuardianStudentPlan.objects.all()

    def resolve_guardian_student_plan_by_guardian_id(self, info, guardian_id):
        # Querying a single question that has guardian_id
        # return GuardianStudentPlan.objects.all().filter(guardian_id=guardian_id, order_detail__is_paid=True, order_detail__is_cancel=False)
        return GuardianStudentPlan.objects.all().filter(guardian_id=guardian_id)


    def resolve_guardian_student_plan_by_id(self, info, id):
        # Querying a single question
        return GuardianStudentPlan.objects.get(pk=id)

    # ----------------- StudentPlan ----------------- #

    students_plan = graphene.List(StudentPlanSchema)
    student_plan_by_id = graphene.Field(
    StudentPlanSchema, id=graphene.String())

    def resolve_students_plan(root, info, **kwargs):
        # Querying a list
        return StudentPlan.objects.all()

    def resolve_student_plan_by_id(root, info, id):
        # Querying a single question
        return StudentPlan.objects.get(pk=id)

    # # ----------------- StudentPlanTopicGrade ----------------- #

    # students_plan_topic_grade = graphene.List(StudentPlanTopicGradeSchema)
    # student_plan_topic_grade_by_id = graphene.Field(
    #     StudentPlanTopicGradeSchema, id=graphene.String())

    # def resolve_students_plan_topic_grade(root, info, **kwargs):
    #     # Querying a list
    #     return StudentPlanTopicGrade.objects.all()

    # def resolve_student_plan_topic_grade_by_id(root, info, id):
    #     # Querying a single question
    #     return StudentPlanTopicGrade.objects.get(pk=id)
