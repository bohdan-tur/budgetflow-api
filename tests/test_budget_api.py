from datetime import date, timedelta

import pytest
from rest_framework import status

from finance.models import Budget
from tests.factories import BudgetFactory, CategoryFactory

pytestmark = pytest.mark.django_db


def test_get_budget_list(auth_client, budget):
    response = auth_client.get("/api/budgets/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == budget.id


def test_get_budget_list_returns_only_user_budgets(auth_client, user):
    BudgetFactory(user=user)
    BudgetFactory()

    response = auth_client.get("/api/budgets/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


def test_get_budget_detail(auth_client, budget):
    response = auth_client.get(f"/api/budgets/{budget.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == budget.id
    assert response.data["amount"] == str(budget.amount)


def test_get_budget_detail_other_user(auth_client):
    budget = BudgetFactory()

    response = auth_client.get(f"/api/budgets/{budget.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_budget(auth_client, expense_category):
    payload = {
        "category": expense_category.id,
        "amount": 1000,
        "start_date": date.today(),
        "end_date": date.today() + timedelta(days=30),
    }

    response = auth_client.post(
        "/api/budgets/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["category"] == expense_category.id
    assert response.data["amount"] == "1000.00"


def test_create_budget_other_user_category(auth_client):
    category = CategoryFactory()

    payload = {
        "category": category.id,
        "amount": 1000,
        "start_date": date.today(),
        "end_date": date.today() + timedelta(days=30),
    }

    response = auth_client.post(
        "/api/budgets/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_budget_invalid_data(auth_client):
    payload = {
        "amount": 1000,
    }

    response = auth_client.post(
        "/api/budgets/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_budget(auth_client, budget):
    response = auth_client.patch(
        f"/api/budgets/{budget.id}/",
        {
            "amount": 2000,
        },
        format="json",
    )

    budget.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert budget.amount == 2000


def test_update_budget_other_user_category(auth_client, budget):
    category = CategoryFactory()

    response = auth_client.patch(
        f"/api/budgets/{budget.id}/",
        {
            "category": category.id,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_other_user_budget(auth_client):
    budget = BudgetFactory()

    response = auth_client.patch(
        f"/api/budgets/{budget.id}/",
        {
            "amount": 5000,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_nonexistent_budget(auth_client):
    response = auth_client.patch(
        "/api/budgets/99999/",
        {
            "amount": 5000,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_budget(auth_client, budget):
    budget_id = budget.id

    response = auth_client.delete(f"/api/budgets/{budget_id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Budget.objects.filter(id=budget_id).exists()


def test_delete_other_user_budget(auth_client):
    budget = BudgetFactory()

    response = auth_client.delete(f"/api/budgets/{budget.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_budget(auth_client):
    response = auth_client.delete("/api/budgets/99999/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_unauthorized_get_budgets(api_client):
    response = api_client.get("/api/budgets/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthorized_create_budget(api_client, expense_category):
    response = api_client.post(
        "/api/budgets/",
        {
            "category": expense_category.id,
            "amount": 1000,
            "start_date": date.today(),
            "end_date": date.today() + timedelta(days=30),
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
