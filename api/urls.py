from django.urls import path,include
from rest_framework.routers import DefaultRouter
from finance.views.wallet import WalletViewSet
from finance.views.category import CategoryViewSet
from finance.views.transaction import TransactionViewSet
from finance.views.transfer import TransferViewSet
from finance.views.budget import BudgetViewSet
router = DefaultRouter()

router.register('wallets', WalletViewSet, basename="wallet")
router.register('categories', CategoryViewSet, basename="category")
router.register('transactions', TransactionViewSet, basename="transaction")
router.register( "transfers",TransferViewSet, basename="transfer",
)
router.register( "budgets",BudgetViewSet, basename="budget",
)

urlpatterns = [

     path('',include(router.urls)),
     path('auth/',include("users.urls")),


]