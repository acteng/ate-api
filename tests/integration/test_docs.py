import pytest
from starlette.testclient import TestClient

from ate_api.settings import Settings

pytestmark = pytest.mark.parametrize("path", ["/openapi.json", "/docs"])


class TestDocsWhenPublic:
    def test_can_access(self, client: TestClient, path: str) -> None:
        response = client.get(path)

        assert response.status_code == 200


class TestDocsWhenProtected:
    @pytest.fixture(name="settings")
    def settings_fixture(self, settings: Settings) -> Settings:
        return settings.model_copy(update={"docs_username": "boardman", "docs_password": "letmein"})

    def test_can_access_with_correct_credentials(self, client: TestClient, path: str) -> None:
        # echo -n 'boardman:letmein' | base64
        response = client.get(path, headers={"Authorization": "Basic Ym9hcmRtYW46bGV0bWVpbg=="})

        assert response.status_code == 200

    def test_cannot_access_with_incorrect_credentials(self, client: TestClient, path: str) -> None:
        # echo -n 'obree:opensesame' | base64
        response = client.get(path, headers={"Authorization": "Basic b2JyZWU6b3BlbnNlc2FtZQ=="})

        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == "Basic"
        assert response.json() == {"detail": "Unauthorized"}

    def test_cannot_access_without_credentials(self, client: TestClient, path: str) -> None:
        response = client.get(path)

        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == "Basic"
        assert response.json() == {"detail": "Not authenticated"}
