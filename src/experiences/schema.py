import graphene
from django.conf import settings
from graphene_django import DjangoObjectType
from experiences.models import Level, Battery


class LevelSchema(DjangoObjectType):
    class Meta:
        model = Level
        fields = "__all__"

    name = graphene.String()

    def resolve_name(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter("name", language_code=current_language)


class BatterySchema(DjangoObjectType):
    class Meta:
        model = Battery
        fields = "__all__"


class Query(graphene.ObjectType):
    levels = graphene.List(LevelSchema)
    level_by_id = graphene.Field(LevelSchema, id=graphene.String())
    next_level = graphene.Field(LevelSchema)
    next_level_by_amount = graphene.Field(LevelSchema,  amount=graphene.Int())

    def resolve_levels(root, info, **kwargs):
        # Querying a list
        return Level.objects.all()

    def resolve_level_by_id(root, info, id):
        # Querying a single level
        return Level.objects.get(pk=id)

    def resolve_next_level(root, info) :
        """ Get current user's next level"""
        # Get user from token
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")
        # Get current level of user
        current_level = user.student.level
        # Get next level of user
        next_level = current_level.get_next_level()
        return next_level
    
    def resolve_next_level_by_amount(root, info, amount) :
        """ Get next level from specific level's amount"""
        current_level = Level.objects.get(amount = amount)
        next_level = current_level.get_next_level()
        return next_level
