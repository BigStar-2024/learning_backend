from unicodedata import category
import graphene
from graphene_django import DjangoObjectType
from .models import Game, PlayGameTransaction, GameCategory
from django.conf import settings


class GameSchema(DjangoObjectType):
    class Meta:
        model = Game
        fields = "__all__"

    name = graphene.String()

    def resolve_name(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "name", language_code=current_language)


class PlayGameTransactionSchema(DjangoObjectType):
    class Meta:
        model = PlayGameTransaction
        fields = "__all__"


class GameCategorySchema(DjangoObjectType):
    class Meta:
        model = GameCategory
        fields = "__all__"
    
    name = graphene.String()

    def resolve_name(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "name", language_code=current_language)


class Query(graphene.ObjectType):
    # ----------------- GameCategory ----------------- #

    games_category = graphene.List(GameCategorySchema)
    game_category_by_id = graphene.Field(
        GameCategorySchema, id=graphene.ID())


    def resolve_games_category(root, info, **kwargs):
        # Querying a list
        return GameCategory.objects.all()


    def resolve_game_category_by_id(root, info, id):
        # Querying a single game category
        return GameCategory.objects.get(pk=id)
    

    # ----------------- Game ----------------- #

    games = graphene.List(GameSchema)
    game_by_id = graphene.Field(GameSchema, id=graphene.ID())
    def resolve_games(root, info, **kwargs):
        # Querying a list
        return Game.objects.all()


    def resolve_game_by_id(root, info, id):
        # Querying a single game by id
        return Game.objects.get(pk=id)


    # ----------------- Games by Category ID ----------------- #

    games_by_category_id = graphene.List(GameSchema, category=graphene.ID())

    def resolve_games_by_category_id(root, info, category):
        # Querying a game list by category
        return Game.objects.filter(category=category)
    

    # ----------------- Games by Category Name ----------------- #

    games_by_category_name = graphene.List(GameSchema, category_name=graphene.String())

    def resolve_games_by_category_name(root, info, category_name):
        # Querying a game list by category Name
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return Game.objects.filter(category__translations__name=category_name, category__translations__language_code=current_language)

    # ----------------- Play game transactions ------------------------#
    play_game_transactions = graphene.List(PlayGameTransactionSchema)

    def resolve_play_game_transactions(root, info):
        # Querying a game list by category Name
        return PlayGameTransaction.objects.all()
