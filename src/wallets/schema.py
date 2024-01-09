import graphene
from graphene_django import DjangoObjectType
from .models import CoinWallet
from accounting.models import Movement
from block.models import BlockTransaction


class CoinWalletSchema(DjangoObjectType):
    class Meta:
        model = CoinWallet
        fields = "__all__"

    block_transaction_coins = graphene.Int()

    def resolve_block_transaction_coins(self, info):
        return self.block_transaction_aggregate


class BlockTransactionSchema():
    class Meta:
        model = BlockTransaction
        fields = "__all__"


class CoinWalletTransactionSchema(DjangoObjectType):
    class Meta:
        model = Movement
        fields = "__all__"

    description = graphene.String()

    def resolve_description(self, info):
        subclass = Movement.objects.filter(pk=self.id).get_subclass()
        subclass_name = subclass.__class__.__name__
        return subclass_name


class Query(graphene.ObjectType):
    # ----------------- CoinWallet ----------------- #

    coin_wallets = graphene.List(CoinWalletSchema)
    coin_wallet_by_id = graphene.Field(CoinWalletSchema, id=graphene.ID())
    coin_wallet_transactions_by_id = graphene.List(CoinWalletTransactionSchema, student_id=graphene.ID())
    coin_wallet_block_transactions = graphene.List(CoinWalletSchema)

    def resolve_coin_wallets(root, info, **kwargs):
        # Querying a list
        return CoinWallet.objects.all()

    def resolve_coin_wallet_by_id(root, info, id):
        # Querying a single question
        return CoinWallet.objects.get(pk=id)

    def resolve_coin_wallet_transactions_by_id(root, info, student_id):
        # Querying wallet transaction
        recent_transactions = Movement.objects\
            .filter(account__student=student_id)[:200]
        return recent_transactions

    def resolve_coin_wallet_by_id(root, info):
        return sorted(CoinWallet.objects.all(), key=lambda c: c.block_transaction_aggregate)
