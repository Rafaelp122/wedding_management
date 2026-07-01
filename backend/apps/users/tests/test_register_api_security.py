import pytest


@pytest.mark.django_db
def test_register_user_weak_password_api_response(auth_client):
    """
    Testa se o endpoint de registro retorna uma mensagem de erro amigável (400)
    quando a validação de senha falha.
    """
    response = auth_client.post(
        "/api/v1/auth/register/",
        {
            "email": "weak-api@example.com",
            "password": "password",
            "first_name": "Weak",
            "last_name": "API",
            "company_name": "Test Co",
        },
        content_type="application/json",
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "code" in data
    assert data["code"] == "validation_error"
    # A mensagem vem do CommonPasswordValidator do Django
    assert "Esta senha é muito comum." in str(data["detail"])
