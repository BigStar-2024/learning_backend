import graphene
from graphene_django import DjangoObjectType
from .models import Badge, StudentBadge


class BadgeSchema(DjangoObjectType):
    class Meta:
        model = Badge
        fields = "__all__"

class StudentBadgeSchema(DjangoObjectType):
    class Meta:
        model = StudentBadge
        fields = "__all__"


class Query(graphene.ObjectType):
    # ----------------- Badge ----------------- #

    badges = graphene.List(BadgeSchema)
    badges_by_id = graphene.Field(BadgeSchema, id=graphene.ID())
    badges_by_student_id = graphene.List(BadgeSchema, id=graphene.ID())
    def resolve_badges(root, info, **kwargs):
        # Querying a list
        return Badge.objects.all()

    def resolve_badges_by_id(root, info, id):
        # Querying a single badge
        return Badge.objects.get(pk=id)

    def resolve_badges_by_student_id(root, info, id):
        # Querying a badge that student owned
        return Badge.objects.filter(studentbadge__student__id = id)

    # --------------- Student Badge ------------ #
    student_badges = graphene.List(StudentBadgeSchema)
    student_badges_by_student_id = graphene.List(StudentBadgeSchema, id=graphene.ID())

    def resolve_student_badges(root, info, **kwargs):
        # Querying a single question
        return StudentBadge.objects.all()

    def resolve_student_badges_by_student_id(root, info, id):
        # Querying a single question
        return StudentBadge.objects.filter(student__id=id)

    #--------------- Badges by Student ID --------- #

