import graphene
from graphene_django import DjangoObjectType
from universals.models import UniversalAreaOfKnowledge, UniversalTopic


class UniversalAreaOfKnowledgeSchema(DjangoObjectType):
    class Meta:
        model = UniversalAreaOfKnowledge
        fields = "__all__"


class UniversalTopicSchema(DjangoObjectType):
    class Meta:
        model = UniversalTopic
        fields = "__all__"


class Query(graphene.ObjectType):
    # ----------------- UniversalAreaOfKnowledge ----------------- #

    universals_area_of_knowledge = graphene.List(
        UniversalAreaOfKnowledgeSchema)
    universal_area_of_knowledge_by_id = graphene.Field(
        UniversalAreaOfKnowledgeSchema, id=graphene.String())

    def resolve_universals_area_of_knowledge(root, info, **kwargs):
        # Querying a list
        return UniversalAreaOfKnowledge.objects.all()

    def resolve_universal_area_of_knowledge_by_id(root, info, id):
        # Querying a single question
        return UniversalAreaOfKnowledge.objects.get(pk=id)

    # ----------------- UniversalTopic ----------------- #

    universals_topic = graphene.List(UniversalTopicSchema)
    universal_topic_by_id = graphene.Field(
        UniversalTopicSchema, id=graphene.String())

    def resolve_universals_topic(root, info, **kwargs):
        # Querying a list
        return UniversalTopic.objects.all()

    def resolve_universal_topic_by_id(root, info, id):
        # Querying a single question
        return UniversalTopic.objects.get(pk=id)
