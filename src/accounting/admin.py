from django.contrib import admin
from .models import (
    Account,
    Movement,
    PositiveMovement,
    NegativeMovement,
    BankMovement,
    BankPositiveMovement,
    BankNegativeMovement
)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'positive_side', 'balance')
    search_fields = ('id', 'name', 'positive_side')
    ordering = ('name',)
    readonly_fields = ()

    filter_horizontal = ()
    list_filter = ('positive_side', 'balance')
    fieldsets = ()


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ('account', 'date', 'side', 'comment', 'amount')
    search_fields = ('id', 'account__student__full_name', 'comment', 'amount')
    ordering = ('-date', '-pk')
    readonly_fields = ('date',)

    filter_horizontal = ()
    list_filter = ('side', 'date', 'amount')
    fieldsets = ()


@admin.register(BankMovement)
class BankMovementAdmin(admin.ModelAdmin):
    list_display = ('account', 'date', 'side', 'comment', 'amount')
    search_fields = ('id', 'account__student__full_name', 'comment', 'amount')
    ordering = ('-date', '-pk')
    readonly_fields = ('date',)

    filter_horizontal = ()
    list_filter = ('side', 'date', 'amount')
    fieldsets = ()


@admin.register(PositiveMovement)
class PositiveMovementAdmin(admin.ModelAdmin):
    list_display = ('account', 'date', 'side', 'comment', 'amount')
    search_fields = ('id', 'account__student__full_name', 'comment', 'amount')
    ordering = ('-date', '-pk')
    readonly_fields = ('date',)

    filter_horizontal = ()
    list_filter = ('side', 'date', 'amount')
    fieldsets = ()


@admin.register(NegativeMovement)
class NegativeMovementAdmin(admin.ModelAdmin):
    list_display = ('account', 'date', 'side', 'comment', 'amount')
    search_fields = ('id', 'account__student__full_name', 'comment', 'amount')
    ordering = ('-date', '-pk')
    readonly_fields = ('date',)

    filter_horizontal = ()
    list_filter = ('side', 'date', 'amount')
    fieldsets = ()


@admin.register(BankPositiveMovement)
class BankPositiveMovementAdmin(admin.ModelAdmin):
    list_display = ('account', 'date', 'side', 'comment', 'amount')
    search_fields = ('id', 'account__student__full_name', 'comment', 'amount')
    ordering = ('-date', '-pk')
    readonly_fields = ('date',)

    filter_horizontal = ()
    list_filter = ('side', 'date', 'amount')
    fieldsets = ()


@admin.register(BankNegativeMovement)
class BankNegativeMovementAdmin(admin.ModelAdmin):
    list_display = ('account', 'date', 'side', 'comment', 'amount')
    search_fields = ('id', 'account__student__full_name', 'comment', 'amount')
    ordering = ('-date', '-pk')
    readonly_fields = ('date',)

    filter_horizontal = ()
    list_filter = ('side', 'date', 'amount')
    fieldsets = ()
