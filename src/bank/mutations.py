from accounting.models import Account
import graphene
from wallets.models import CoinWallet
from students.models import Student
from students.schema import StudentSchema
from bank.models import (
    BankWallet,
)
from accounting.models import BankMovement
from .schema import BankMovementSchema
from graphql import GraphQLError
from wallets.models import (Withdraw, Deposit)

SIDE_CHOICE_DEPOSIT = 'R'
SIDE_CHOICE_WITHDRAW = 'L'

class BankAccountDeposit(graphene.Mutation):
    """ Bank Transaction """
    student = graphene.Field(StudentSchema)
    bankMovement = graphene.Field(BankMovementSchema)
    class Arguments:
        amount = graphene.Float(required=True)

    def mutate(self, info, amount):
        # student = Student.objects.get(id=student)
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")
        student = info.context.user.student
        bank_balance = student.bankWallet.balance
        wallet_balance = student.coinWallet.balance
        print(bank_balance,amount, wallet_balance, type(amount))
        if wallet_balance > amount:
            #----------------- Deposit coins to bank by create bank deposit transaction -S-----------------------#
            bank_account, ba_new = BankWallet.objects.get_or_create(student=student)
            bank_deposit = BankMovement.objects.create(amount=amount, account=bank_account, side=SIDE_CHOICE_DEPOSIT)
            #----------------- Deposit coins to bank by create bank deposit transaction -E-----------------------#

            #----------------- Withdraw coins from wallet by create wallet withdraw transaction -S---------------#
            coinWalletTransaction = Withdraw(
                amount=amount,
                account = student.coinWallet
            )
            coinWalletTransaction.save()
            student.bankWallet = bank_deposit.account
            student.coinWallet = coinWalletTransaction.account
            #----------------- Withdraw coins from wallet by create wallet withdraw transaction -E---------------#

            return BankAccountDeposit(student=student, bankMovement=bank_deposit)
        
        raise GraphQLError('Insufficient balance')


class BankAccountWithdraw(graphene.Mutation):
    """ Bank Transaction """
    student = graphene.Field(StudentSchema)
    bankMovement = graphene.Field(
        BankMovementSchema)

    class Arguments:
        amount = graphene.Float(required=True)

    def mutate(self, info, amount):
        # student = Student.objects.get(id=student)
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")
        student = info.context.user.student
        bank_balance = student.bankWallet.balance

        if bank_balance > amount:
            #----------------- Withdraw coins from bank by create bank deposit transaction -S-----------------------#
            bank_account, ba_new = BankWallet.objects.get_or_create(student=student)
            bank_withdraw = BankMovement.objects.create(amount=amount, account=bank_account, side=SIDE_CHOICE_WITHDRAW)
            #----------------- Withdraw coins from bank by create bank deposit transaction -E-----------------------#

            #----------------- Deposit coins to wallet by create wallet withdraw transaction -S---------------#
            coinWalletTransaction = Deposit(
                amount=amount,
                account = student.coinWallet
            )
            coinWalletTransaction.save()
            #----------------- Deposit coins to wallet by create wallet withdraw transaction -E---------------#
            print(bank_account.get_balance_aggregate())
            student.bankWallet = bank_withdraw.account
            student.coinWallet = coinWalletTransaction.account

            return BankAccountWithdraw(
                bankMovement=bank_withdraw,
                student=student
            )
        raise GraphQLError('Insufficient balance')


class Mutation(graphene.ObjectType):
    BankAccountDeposit = BankAccountDeposit.Field()
    BankAccountWithdraw = BankAccountWithdraw.Field()