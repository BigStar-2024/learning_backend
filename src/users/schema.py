import graphene
from graphene_django import DjangoObjectType
from api.models import profile
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class UserSchema(DjangoObjectType):
    language = graphene.String()

    def resolve_language(self, info):
        return self.language

    class Meta:
        model = get_user_model()


class UserProfileSchema(DjangoObjectType):
    class Meta:
        model = profile


class Query(graphene.ObjectType):

    # ----------------- User ----------------- #

    users = graphene.List(UserSchema)
    user_by_id = graphene.Field(UserSchema, id=graphene.ID())

    def resolve_users(root, info, **kwargs):
        # Querying a list
        return get_user_model().objects.all()

    def resolve_user_by_id(root, info, id):
        # Querying a single question
        return get_user_model().objects.get(pk=id)
