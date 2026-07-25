from django.urls import path,include
from rest_framework.routers import DefaultRouter
from finance.views.wallet import WalletViewSet
from finance.views.category import CategoryViewSet

router = DefaultRouter()

router.register('wallets',WalletViewSet,basename = "wallet")
router.register('categories',CategoryViewSet,basename = "category")

urlpatterns = [

     path('',include(router.urls)),
     path('auth/',include("users.urls")),


]