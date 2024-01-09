from django.contrib import admin
from .models import BankWallet, Interest


@admin.register(BankWallet)
class BankWalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'positive_side', 'balance')
    search_fields = ('id', 'student__full_name')
    list_filter = ('positive_side', 'balance', 'student__gender')


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'period', 'requireCoin', 'amount')
    search_fields = ('id', 'name', 'period', 'requireCoin', 'amount')
    list_filter = ('period', 'requireCoin', 'amount')
    