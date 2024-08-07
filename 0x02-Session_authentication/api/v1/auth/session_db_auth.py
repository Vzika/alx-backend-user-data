#!/usr/bin/env python3
"""Session database authentication
"""

from datetime import datetime, timedelta
from api.v1.auth.session_exp_auth import SessionExpAuth
from models.user_session import UserSession


class SessionDBAuth(SessionExpAuth):
    """Session database authentication
    """

    def create_session(self, user_id: str = None) -> str:
        """Creates a session ID
        """
        session_id = super().create_session(user_id)
        if session_id is None:
            return None
        user = {"user_id": user_id, "session_id": session_id}
        user = UserSession(**user)
        user.save()
        return session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """Returns a User ID based on a Session ID
        """
        if session_id is None:
            return None
        user_sessions = UserSession.search({"session_id": session_id})
        if user_sessions:
            user_session = user_sessions[0]
        else:
            return None
        created_at = user_session.created_at
        if self.session_duration <= 0:
            return user_session.user_id
        if not created_at:
            return None
        expires_at = created_at + timedelta(seconds=self.session_duration)
        if datetime.now() > expires_at:
            return None
        return user_session.user_id

    def destroy_session(self, request=None) -> bool:
        """Deletes the user session / logout
        """
        if request is None:
            return False
        session_id = self.session_cookie(request)
        if session_id is None:
            return False
        user_sessions = UserSession.search({"session_id": session_id})
        if user_sessions is None:
            return False
        user_sessions[0].remove()
