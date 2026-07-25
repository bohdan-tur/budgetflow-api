from rest_framework import serializers
from finance.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):


     class Meta:

         model = Transaction

         fields = [
           "id",
          "wallet",
         "category",
         "amount",
         "description",
         "transaction_date",
         "created_at",
         "updated_at",
      ]

         read_only_fields = [

           "id",
           "created_at",
           "updated_at",

       ]

     def validate_wallet(self,wallet):
         if wallet.user != self.context["request"].user:

             raise serializers.ValidationError(
                 "You don't have access to this wallet."
             )
         return wallet

     def validate_category(self,category):

         if category.user != self.context["request"].user:
             raise serializers.ValidationError(
                 "You don't have access to this category."
             )
         return category

