from finance.serializers.transaction import TransactionSerializer
from rest_framework.viewsets import ModelViewSet
from finance.models.transaction import Transaction



class TransactionViewSet(ModelViewSet):

    serializer_class = TransactionSerializer



    def get_queryset(self):

       return Transaction.objects.filter(wallet__user = self.request.user)

