import pytest
from rest_framework import status

from tests.factories import TransactionFactory, WalletFactory

pytestmark = pytest.mark.django_db


def test_get_monthly_report(auth_client, user, income_category, expense_category):
    wallet = WalletFactory(user=user)

    TransactionFactory(
        wallet=wallet,
        category=income_category,
        amount=100,
    )

    TransactionFactory(
        wallet=wallet,
        category=expense_category,
        amount=50,
    )
    response = auth_client.get("/api/reports/monthly_statistics/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    report = response.data[0]

    assert report["income"] == "100.00"
    assert report["expense"] == "50.00"


def test_get_monthly_report_unauthorized(api_client):
    response = api_client.get("/api/reports/monthly_statistics/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
