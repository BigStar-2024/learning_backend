import graphene
from graphene_django import DjangoObjectType
from .models import Notes


class NotesSchema(DjangoObjectType):
    class Meta:
        model = Notes
        fields = "__all__"

class Query(graphene.ObjectType):
    # ----------------- Organization ----------------- #

    notes_of_user_received = graphene.List(
        NotesSchema)
    notes_of_user_sent = graphene.List(
        NotesSchema)

    def resolve_notes_of_user_received(root, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise Exception("Authentication credentials were not provided")

        user = info.context.user

        return Notes.objects.filter(user_to = user).all()

    def resolve_notes_of_user_sent(root, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise Exception("Authentication credentials were not provided")

        user = info.context.user
        
        return Notes.objects.filter(user_from = user).all()

