import graphene
import random
from .schema import CollectibleSchema, CollectiblePurchaseTransactionSchema, CollectiblePackPurchaseTransactionSchema
from .models import Collectible, CollectibleCategory
from .models import CollectiblePurchaseTransaction, CollectiblePackPurchaseTransaction
from students.models import Student
from students.schema import StudentSchema
from wallets.models import CoinWallet


class PurchaseCollectiblePack(graphene.Mutation):
    """ Purchase a collectible pack """
    PACK_SIZE = 3

    COMMON_PROBABILITY = 40
    RARE_PROBABILITY = 30
    LEGENDARY_PROBABILITY = 20
    EPIC_PROBABILITY = 10

    COLLECTIBLE_TIERS_PROBABILITIES = [
        COMMON_PROBABILITY,
        RARE_PROBABILITY,
        LEGENDARY_PROBABILITY,
        EPIC_PROBABILITY,
    ]

    COLLECTIBLE_TIERS = [
        Collectible.COMMON,
        Collectible.RARE,
        Collectible.LEGENDARY,
        Collectible.EPIC
    ]

    student = graphene.Field(StudentSchema)
    collectible_pack_purchase_transaction = graphene.Field(
        CollectiblePackPurchaseTransactionSchema)

    class Arguments:
        student = graphene.ID(required=True)
        collectible_category = graphene.ID(required=True)
        pack_size = graphene.Int(required=False)

    def mutate(
            self,
            info,
            student,
            collectible_category,
            pack_size=PACK_SIZE,
            collectible_tiers=COLLECTIBLE_TIERS,
            collectible_tiers_probabilities=COLLECTIBLE_TIERS_PROBABILITIES):
        # Select student
        student = Student.objects.get(id=student)
        # Get or create student coin wallet account
        account, new = CoinWallet.objects.get_or_create(student=student)
        # Select price from category
        pack_price = CollectibleCategory.objects.get(
            id=collectible_category).price
        if account.balance > pack_price:
            # Create collectible purchase transaction
            collectible_pack_purchase_transaction = CollectiblePackPurchaseTransaction(
                account=account, amount=pack_price)
            collectible_pack_purchase_transaction.save()

            # Initialize selection dict with values in 0
            selection = dict.fromkeys(collectible_tiers, 0)
            # Select tiers with a weight
            choices = random.choices(
                collectible_tiers,
                weights=collectible_tiers_probabilities,
                k=pack_size
            )

            for choice in choices:
                selection[choice] += 1
            for tier, amount in selection.items():
                available_collectibles = list(
                    Collectible.objects.filter(
                        category=collectible_category, tier=tier))
                selected_collectibles = random.sample(
                    available_collectibles, amount)
                collectible_pack_purchase_transaction.collectibles.add(
                    *selected_collectibles)
            collectible_pack_purchase_transaction.save()
            collectible_pack_purchase_transaction.assign_collectibles()

            return PurchaseCollectiblePack(
                collectible_pack_purchase_transaction=collectible_pack_purchase_transaction,
                student=student,
            )
        raise Exception('Your coin is not enough')


class PurchaseCollectible(graphene.Mutation):
    """ Purchase a single collectible """
    collectible_purchase_transaction = graphene.Field(
        CollectiblePurchaseTransactionSchema)
    student = graphene.Field(StudentSchema)
    collectible = graphene.Field(CollectibleSchema)

    class Arguments:
        student = graphene.ID(required=True)
        collectible = graphene.ID(required=True)

    def mutate(self, info, student, collectible):
        student = Student.objects.get(id=student)
        collectible = Collectible.objects.get(id=collectible)
        account, new = CoinWallet.objects.get_or_create(student=student)

        collectible_purchase_transaction = CollectiblePurchaseTransaction(
            collectible=collectible,
            account=account,
        )
        collectible_purchase_transaction.save()

        return PurchaseCollectible(
            collectible_purchase_transaction=collectible_purchase_transaction,
            student=student,
            collectible=collectible,
        )


class Mutation(graphene.ObjectType):
    purchase_collectible = PurchaseCollectible.Field()
    purchase_collectible_pack = PurchaseCollectiblePack.Field()
