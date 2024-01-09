import graphene
from graphql import GraphQLError
from wallets.models import CoinWallet
from students.models import Student
from .models import Game, PlayGameTransaction
from students.schema import StudentSchema
from .schema import PlayGameTransactionSchema, GameSchema


class PlayGame(graphene.Mutation):
    """ play game using wallet coins """
    play_game_transaction = graphene.Field(
        PlayGameTransactionSchema)
    student = graphene.Field(StudentSchema)
    game = graphene.Field(GameSchema)
    gameContent = graphene.String()

    class Arguments:
        game = graphene.ID(required=True)

    def mutate(self, info, game):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")
        
        student = user.student
        game = Game.objects.get(id=game)
        account, new = CoinWallet.objects.get_or_create(student=student)
        if account.balance > game.cost:
            gameContent = game.get_game_content()
            play_game_transaction = PlayGameTransaction(
                game=game,
                account=account,
            )
            play_game_transaction.save()
            game.play_stats += 1
            game.save()

            return PlayGame(
                play_game_transaction=play_game_transaction,
                student=student,
                game=game,
                gameContent=gameContent
            )
        raise GraphQLError('Insufficient balance')

class Mutation(graphene.ObjectType):
    play_game = PlayGame.Field()