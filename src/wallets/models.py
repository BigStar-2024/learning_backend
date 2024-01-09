from django.db import models
from decimal import Decimal
from accounting.models import Account, PositiveMovement, NegativeMovement


class CoinWallet(Account):
    student = models.OneToOneField(
        'students.Student',
        on_delete=models.PROTECT,
        related_name="coinWallet",
        null=True)

    @property
    def block_transaction_aggregate(self):
        positive_movements_aggregate = self.movement_set.filter(
            side=self.positive_side,
            comment="Answer the questions.",
        ).aggregate(models.Sum('amount'))

        positive_movements_balance = positive_movements_aggregate[
            'amount__sum'] if positive_movements_aggregate['amount__sum'] else 0

        return positive_movements_balance


class EngagementWallet(Account):
    student = models.OneToOneField(
        'students.Student',
        on_delete=models.PROTECT,
    )
    current_level = models.PositiveSmallIntegerField(null=True, default=1)


class Deposit(PositiveMovement):
    pass


class Withdraw(NegativeMovement):
    pass
