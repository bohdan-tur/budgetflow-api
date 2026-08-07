from rest_framework import serializers

from finance.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category

        fields = [
            "id",
            "name",
            "type",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_type(self, new_type):
        if self.instance is None or new_type == self.instance.type:
            return new_type

        if self.instance.transactions.exists():
            raise serializers.ValidationError(
                "Category type cannot be changed because it is already "
                "used in transactions."
            )

        if self.instance.budgets.exists():
            raise serializers.ValidationError(
                "Category type cannot be changed because it is already used in budgets."
            )

        return new_type
