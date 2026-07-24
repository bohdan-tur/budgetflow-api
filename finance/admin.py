from django.contrib import admin

from finance.models.category import Category
from finance.models.transaction import Transaction
from finance.models.wallet import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "balance",
        "currency",
    )
    search_fields = (
        "name",
        "user__username",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "type",
    )
    search_fields = (
        "name",
        "user__username",
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "wallet",
        "category",
        "amount",
        "transaction_date",
    )
    list_filter = (
        "category__type",
        "transaction_date",
    )