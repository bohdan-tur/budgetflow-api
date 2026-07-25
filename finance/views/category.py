from rest_framework.viewsets import ModelViewSet
from finance.serializers.category import CategorySerializer
from finance.models.category import Category

class CategoryViewSet(ModelViewSet):

     serializer_class = CategorySerializer



     def get_queryset(self):

         return Category.objects.filter(user = self.request.user)



     def perform_create(self,serializer):

         serializer.save(user = self.request.user)