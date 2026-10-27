import os
import unittest
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from models import Base, User
from routers.auth_router import router
from utils.auth import get_current_user
from utils.security import create_access_token


class LogoutTests(unittest.TestCase):
    def setUp(self):
        self.secret = patch.dict(os.environ, {"JWT_SECRET": "test-secret-" * 5})
        self.secret.start()
        self.engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        Base.metadata.create_all(self.engine)
        factory = sessionmaker(self.engine)
        self.patches = [
            patch("utils.auth.get_session", factory),
        ]
        for item in self.patches:
            item.start()
        with factory() as session:
            session.add(User(id=1, username="test", full_name="Test", role="STUDENT",
                             password_hash="unused-by-authentication-check"))
            session.commit()
        app = FastAPI()
        app.include_router(router)

        @app.get("/protected")
        def protected(user=Depends(get_current_user)):
            return {"id": user.id}

        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        for item in reversed(self.patches):
            item.stop()
        self.secret.stop()
        self.engine.dispose()

    def test_client_side_logout(self):
        token = create_access_token({"sub": "1"})
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/api/auth/logout", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True, "message": "Logout successful"})
        # The client must clear the token; the server does not revoke it.
        self.assertEqual(self.client.get("/protected", headers=headers).status_code, 200)
        self.assertEqual(self.client.get("/protected").status_code, 401)

    def test_logout_rejects_missing_invalid_and_expired_tokens(self):
        expired = jwt.encode(
            {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
            os.environ["JWT_SECRET"], algorithm="HS256",
        )
        for headers in ({}, {"Authorization": "Bearer invalid"},
                        {"Authorization": f"Bearer {expired}"}):
            with self.subTest(headers=headers):
                response = self.client.post("/api/auth/logout", headers=headers)
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.headers["www-authenticate"], "Bearer")

if __name__ == "__main__":
    unittest.main()
