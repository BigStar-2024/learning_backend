from django.db import models
from accounting.models import Account
from app.models import TimestampModel, RandomSlugModel, IsActiveModel
from django.db.models import Q
from datetime import datetime
from decimal import Decimal

class BankWallet(Account):
    student = models.OneToOneField(
        'students.Student',
        on_delete=models.PROTECT,
        related_name="bankWallet",
        null=True)

    #override balance method
    def get_balance_aggregate(self):
        print("get balance")
        positive_movements_aggregate = self.bankmovement_set.filter(
            Q(side=self.positive_side) | Q(side=self.SIDE_CHOICE_RIGHT_INTEREST)).aggregate(models.Sum('amount'))
        negative_movements_aggregate = self.bankmovement_set.filter(side=self.get_negative_side).aggregate(
            models.Sum('amount'))

        positive_movements_balance = positive_movements_aggregate['amount__sum'] if positive_movements_aggregate[
            'amount__sum'] else 0
        negative_movements_balance = negative_movements_aggregate['amount__sum'] if negative_movements_aggregate[
            'amount__sum'] else 0

        dict = {}
        # balance = positive_movements_balance - negative_movements_balance
        balance = positive_movements_balance - negative_movements_balance
        dict['positive_movements_balance'] = positive_movements_balance
        dict['negative_movements_balance'] = negative_movements_balance
        dict['total_movements_balance'] = Decimal(balance)
        return dict

class Interest(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'interest_'

    name = models.CharField(max_length=64, null=False)
    period = models.IntegerField(null=False, default=0)
    requireCoin = models.IntegerField(null=False, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)