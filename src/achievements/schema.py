import graphene
from django.conf import settings
from graphene_django import DjangoObjectType
from achievements.models import Achievement


class AchievementSchema(DjangoObjectType):
    class Meta:
        model = Achievement
        fields = "__all__"

    name = graphene.String()

    def resolve_name(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter("name", language_code=current_language)


class Query(graphene.ObjectType):
    Achievements = graphene.List(AchievementSchema)
    Achievement_by_id = graphene.Field(AchievementSchema, id=graphene.String())

    def resolve_achievements(root, info, **kwargs):
        # Querying a list
        return Achievement.objects.all()

    def resolve_achievement_category_by_id(root, info, id):
        # Querying a single question
        return Achievement.objects.get(pk=id)
