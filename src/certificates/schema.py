import graphene
from graphene_django import DjangoObjectType
from .models import Certificates, StudentCertificates


class CertificatesSchema(DjangoObjectType):
    class Meta:
        model = Certificates
        fields = "__all__"


class StudentCertificatesSchema(DjangoObjectType):
    class Meta:
        model = StudentCertificates
        fields = "__all__"


class Query(graphene.ObjectType):
    # ----------------- Certificates ----------------- #
    certificates = graphene.List(CertificatesSchema)
    certificates_by_id = graphene.Field(CertificatesSchema, id=graphene.ID())

    def resolve_certificates(root, info, **kwargs):
        return Certificates.objects.all()

    def resolve_certificates_by_id(root, info, id):
        return Certificates.objects.get(pk=id)

    # ----------------- StudentCertificates ----------------- #
    student_certificates = graphene.List(StudentCertificatesSchema)
    student_certificates_by_id = graphene.Field(StudentCertificatesSchema, id=graphene.ID())

    def resolve_student_certificates(root, info, **kwargs):
        return StudentCertificates.objects.all()

    def resolve_student_certificates_by_id(root, info, id):
        return StudentCertificates.objects.get(pk=id)
