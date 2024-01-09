import graphene
from django.conf import settings
from graphene_django import DjangoObjectType
from audiences.models import Audience


class AudienceSchema(DjangoObjectType):
    class Meta:
        model = Audience
        fields = "__all__"

    name = graphene.String()

    def resolve_name(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter("name", language_code=current_language)


class Query(graphene.ObjectType):
    audiences = graphene.List(AudienceSchema)
    audience_by_id = graphene.Field(AudienceSchema, id=graphene.String())

    def resolve_audiences(root, info, **kwargs):
        # Querying a list
        return Audience.objects.all()

    def resolve_audience_by_id(root, info, id):
        # Querying a single question
        return Audience.objects.get(pk=id)
