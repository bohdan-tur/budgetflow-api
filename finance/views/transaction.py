from finance.serializers.transaction import TransactionSerializer
from rest_framework.viewsets import ModelViewSet
from finance.models.transaction import Transaction
from django.db import transaction
from finance.models.choices import CategoryType

class TransactionViewSet(ModelViewSet):

    serializer_class = TransactionSerializer



    def get_queryset(self):

       return Transaction.objects.filter(wallet__user = self.request.user).select_related("wallet", "category")

    def perform_create(self, serializer):
        with transaction.atomic():
            transaction_obj = serializer.save()

            wallet = transaction_obj.wallet

            category = transaction_obj.category

            if category.type == CategoryType.INCOME:

                wallet.balance += transaction_obj.amount

            elif category.type == CategoryType.EXPENSE:

                wallet.balance -= transaction_obj.amount

            wallet.save()


