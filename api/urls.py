from django.urls import path,include
from rest_framework.routers import DefaultRouter
from finance.views.wallet import WalletViewSet


router = DefaultRouter()

router.register('wallets',WalletViewSet,basename = "wallet")


urlpatterns = [

     path('',include(router.urls)),
     path('auth/',include("users.urls")),


]