import graphene
from graphene_django import DjangoObjectType
from .models import TopicStudentReport, AreaOfKnowledgeStudentReport


class TopicStudentReportSchema(DjangoObjectType):
    class Meta:
        model = TopicStudentReport
        fields = "__all__"


class AreaOfKnowledgeStudentReportSchema(DjangoObjectType):
    class Meta:
        model = AreaOfKnowledgeStudentReport
        fields = "__all__"


class Query(graphene.ObjectType):
    topic_student_reports = graphene.List(TopicStudentReportSchema)
    topic_student_report_by_student = graphene.List(
        TopicStudentReportSchema,
        student_id=graphene.ID()
    )

    def resolve_topic_student_report(root, info):
        return TopicStudentReport.objects.all()

    def resolve_topic_student_report_by_student(root, info, student_id):
        pass
