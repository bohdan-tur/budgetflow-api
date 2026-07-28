from rest_framework.viewsets import ModelViewSet

from finance.models.category import Category
from finance.serializers.category import CategorySerializer


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):

        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):

        serializer.save(user=self.request.user)
