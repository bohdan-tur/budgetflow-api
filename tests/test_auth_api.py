import pytest
from rest_framework import status


@pytest.mark.django_db
def test_refresh_token_is_rotated_and_old_token_is_blacklisted(api_client, user):
    token_response = api_client.post(
        "/api/auth/token/",
        {
            "username": user.username,
            "password": "password123",
        },
        format="json",
    )
    assert token_response.status_code == status.HTTP_200_OK

    original_refresh = token_response.data["refresh"]

    refresh_response = api_client.post(
        "/api/auth/token/refresh/",
        {"refresh": original_refresh},
        format="json",
    )

    assert refresh_response.status_code == status.HTTP_200_OK
    assert "access" in refresh_response.data
    assert "refresh" in refresh_response.data
    assert refresh_response.data["refresh"] != original_refresh

    reused_token_response = api_client.post(
        "/api/auth/token/refresh/",
        {"refresh": original_refresh},
        format="json",
    )

    assert reused_token_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert reused_token_response.data["code"] == "token_not_valid"

    rotated_token_response = api_client.post(
        "/api/auth/token/refresh/",
        {"refresh": refresh_response.data["refresh"]},
        format="json",
    )

    assert rotated_token_response.status_code == status.HTTP_200_OK
