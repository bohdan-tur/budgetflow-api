from django.urls import path,include
from rest_framework.routers import DefaultRouter
from finance.views.wallet import WalletViewSet
from finance.views.category import CategoryViewSet
from finance.views.transaction import TransactionViewSet
from finance.views.transfer import TransferViewSet
router = DefaultRouter()

router.register('wallets', WalletViewSet, basename="wallet")
router.register('categories', CategoryViewSet, basename="category")
router.register('transactions', TransactionViewSet, basename="transaction")
router.register( "transfers",TransferViewSet, basename="transfer",
)

urlpatterns = [

     path('',include(router.urls)),
     path('auth/',include("users.urls")),


]