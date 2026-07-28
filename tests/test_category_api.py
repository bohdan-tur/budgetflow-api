import pytest
from rest_framework import status
from rest_framework.test import APIClient

from finance.models.choices import CategoryType
from tests.factories import CategoryFactory

pytestmark = pytest.mark.django_db


def test_get_category_list(auth_client, income_category):
    response = auth_client.get("/api/categories/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == income_category.id


def test_get_category_list_returns_only_user_categories(auth_client, user):
    CategoryFactory(user=user)
    CategoryFactory()

    response = auth_client.get("/api/categories/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


def test_get_category_detail(auth_client, income_category):
    response = auth_client.get(f"/api/categories/{income_category.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == income_category.id
    assert response.data["name"] == income_category.name
    assert response.data["type"] == income_category.type


def test_get_category_detail_other_user(auth_client):
    category = CategoryFactory()

    response = auth_client.get(f"/api/categories/{category.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_category(auth_client):
    payload = {
        "name": "Salary",
        "type": CategoryType.INCOME,
    }

    response = auth_client.post(
        "/api/categories/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Salary"
    assert response.data["type"] == CategoryType.INCOME


def test_create_category_invalid_data(auth_client):
    payload = {
        "type": CategoryType.INCOME,
    }

    response = auth_client.post(
        "/api/categories/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_category(auth_client, income_category):
    response = auth_client.patch(
        f"/api/categories/{income_category.id}/",
        {
            "name": "Updated",
        },
        format="json",
    )

    income_category.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert income_category.name == "Updated"


def test_update_other_user_category(auth_client):
    category = CategoryFactory()

    response = auth_client.patch(
        f"/api/categories/{category.id}/",
        {
            "name": "Hack",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_category(auth_client, expense_category):
    response = auth_client.delete(
        f"/api/categories/{expense_category.id}/"
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_other_user_category(auth_client):
    category = CategoryFactory()

    response = auth_client.delete(
        f"/api/categories/{category.id}/"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_unauthorized_get_categories(api_client):
    response = api_client.get("/api/categories/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthorized_create_category(api_client):
    response = api_client.post(
        "/api/categories/",
        {
            "name": "Salary",
            "type": CategoryType.INCOME,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED