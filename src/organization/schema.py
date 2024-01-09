import graphene
from graphene_django import DjangoObjectType
from organization.models import Organization, OrganizationPersonnel, Group, School, SchoolPersonnel, AdministrativePersonnel, Teacher, Classroom
from organization.models.schools import SchoolAdministrativePersonnel, SchoolSubscriber, SchoolTeacher, Subscriber, TeacherClassroom
from block.models import StudentBlockQuestionPresentationHistory

from payments.models import PaymentMethod


class OrganizationSchema(DjangoObjectType):
    class Meta:
        model = Organization
        fields = "__all__"


class OrganizationPersonnelSchema(DjangoObjectType):
    class Meta:
        model = OrganizationPersonnel
        fields = "__all__"


class GroupSchema(DjangoObjectType):
    class Meta:
        model = Group
        fields = "__all__"


class SchoolSchema(DjangoObjectType):
    class Meta:
        model = School
        fields = "__all__"
    payment_method = graphene.Field('payments.schema.PaymentMethodSchema')

    def resolve_payment_method(self, info):
        payment_method = PaymentMethod.objects.filter(
            is_default=True, school_id=self.id)
        if payment_method.count() != 0:
            return payment_method[0]
        return


class SchoolPersonnelSchema(DjangoObjectType):
    class Meta:
        model = SchoolPersonnel
        fields = "__all__"


class AdministrativePersonnelSchema(DjangoObjectType):
    class Meta:
        model = AdministrativePersonnel
        fields = "__all__"


class TeacherSchema(DjangoObjectType):
    class Meta:
        model = Teacher
        fields = "__all__"
    classrooms = graphene.List('organization.schema.ClassroomSchema')

    payment_method = graphene.Field('payments.schema.PaymentMethodSchema')

    def resolve_classrooms(self, info):
        return Classroom.objects.filter(teacherclassroom__teacher=self)

    def resolve_payment_method(self, info):
        payment_method = PaymentMethod.objects.filter(
            is_default=True, teacher_id=self.id)
        if payment_method.count() != 0:
            return payment_method[0]
        return


class SubscriberSchema(DjangoObjectType):
    class Meta:
        model = Subscriber
        fields = "__all__"


class SchoolSubscriberSchema(DjangoObjectType):
    class Meta:
        model = SchoolSubscriber
        fields = "__all__"


class ClassroomSchema(DjangoObjectType):
    class Meta:
        model = Classroom
        fields = "__all__"

    is_empty = graphene.Boolean()

    def resolve_is_empty(self, info, language_code=None):
        return self.isEmpty


class TeacherClassroomSchema(DjangoObjectType):
    class Meta:
        model = TeacherClassroom
        fields = "__all__"


class SchoolTeacherSchema(DjangoObjectType):
    class Meta:
        model = SchoolTeacher
        fields = "__all__"


class SchoolAdministrativePersonnelSchema(DjangoObjectType):
    class Meta:
        model = SchoolAdministrativePersonnel
        fields = "__all__"


class Query(graphene.ObjectType):
    # ----------------- Organization ----------------- #

    organizations = graphene.List(OrganizationSchema)
    organization_by_id = graphene.Field(
        OrganizationSchema, id=graphene.String())

    def resolve_organizations(root, info, **kwargs):
        # Querying a list
        return Organization.objects.all()

    def resolve_organization_by_id(root, info, id):
        # Querying a single question
        return Organization.objects.get(pk=id)

    # ----------------- OrganizationPersonnel ----------------- #

    organizations_personnel = graphene.List(OrganizationPersonnelSchema)
    organization_personnel_by_id = graphene.Field(
        OrganizationPersonnelSchema, id=graphene.String())

    def resolve_organizations_personnel(root, info, **kwargs):
        # Querying a list
        return OrganizationPersonnel.objects.all()

    def resolve_organization_personnel_by_id(root, info, id):
        # Querying a single question
        return OrganizationPersonnel.objects.get(pk=id)

    # ----------------- Group ----------------- #

    groups = graphene.List(GroupSchema)
    group_by_id = graphene.Field(GroupSchema, id=graphene.ID())
    groups_by_school_id = graphene.List(GroupSchema, school_id=graphene.ID())

    def resolve_groups(root, info, **kwargs):
        # Querying a list
        return Group.objects.all()

    def resolve_group_by_id(root, info, id):
        # Querying a single question
        return Group.objects.get(pk=id)

    def resolve_groups_by_school_id(root, info, school_id):
        # Querying a single question
        return Group.objects.filter(classroom_id=school_id)

    # ----------------- School ----------------- #

    schools = graphene.List(SchoolSchema)
    school_by_id = graphene.Field(SchoolSchema, id=graphene.String())

    def resolve_schools(root, info, **kwargs):
        # Querying a list
        return School.objects.all()

    def resolve_school_by_id(root, info, id):
        # Querying a single question
        return School.objects.get(pk=id)

    # ----------------- SchoolPersonnel ----------------- #

    schools_personnel = graphene.List(SchoolPersonnelSchema)
    school_personnel_by_id = graphene.Field(
        SchoolPersonnelSchema, id=graphene.String())

    def resolve_schools_personnel(root, info, **kwargs):
        # Querying a list
        return SchoolPersonnel.objects.all()

    def resolve_school_personnel_by_id(root, info, id):
        # Querying a single question
        return SchoolPersonnel.objects.get(pk=id)

    # ----------------- AdministrativePersonnel ----------------- #

    administrative_personnel = graphene.List(AdministrativePersonnelSchema)
    administrative_personnel_by_id = graphene.Field(
        AdministrativePersonnelSchema, id=graphene.String())

    def resolve_administrative_personnel(root, info, **kwargs):
        # Querying a list
        return AdministrativePersonnel.objects.all()

    def resolve_sadministrative_personnel_by_id(root, info, id):
        # Querying a single question
        return AdministrativePersonnel.objects.get(pk=id)

    # ----------------- Teacher ----------------- #

    teachers = graphene.List(TeacherSchema)
    teacher_by_id = graphene.Field(
        TeacherSchema, id=graphene.String())

    def resolve_teachers(root, info, **kwargs):
        # Querying a list
        return Teacher.objects.all()

    def resolve_teacher_by_id(root, info, id):
        # Querying a single question
        return Teacher.objects.get(pk=id)

    # ----------------- Classroom ----------------- #

    classrooms = graphene.List(ClassroomSchema)
    classroom_by_id = graphene.Field(
        ClassroomSchema, id=graphene.String())

    def resolve_classrooms(root, info, **kwargs):
        # Querying a list
        return Classroom.objects.all()

    def resolve_classroom_by_id(root, info, id):
        # Querying a single question
        return Classroom.objects.get(pk=id)
