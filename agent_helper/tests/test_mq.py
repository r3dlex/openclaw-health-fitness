"""Smoke tests for agent_helper.mq — MQ client for health & fitness agent."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from agent_helper import mq


# ---------------------------------------------------------------------------
# Module-level metadata
# ---------------------------------------------------------------------------

class TestMetadata:
    """Verify that agent discovery metadata includes all required fields."""

    REQUIRED_FIELDS = {"agent_id", "name", "emoji", "description", "capabilities", "workspace"}

    def test_agent_metadata_has_required_fields(self):
        """_AGENT_METADATA must contain all fields expected by the IAMQ protocol."""
        for field in self.REQUIRED_FIELDS:
            assert field in mq._AGENT_METADATA, f"Missing metadata field: {field}"

    def test_capabilities_is_nonempty_list(self):
        """Capabilities must be a non-empty list of strings."""
        caps = mq._AGENT_METADATA["capabilities"]
        assert isinstance(caps, list)
        assert len(caps) > 0
        assert all(isinstance(c, str) for c in caps)

    def test_agent_id_matches_default(self):
        """Default agent ID should be 'health_fitness_agent'."""
        assert mq._AGENT_METADATA["agent_id"] == "health_fitness_agent"


# ---------------------------------------------------------------------------
# _post() / _get() — HTTP helpers return None on connection error
# ---------------------------------------------------------------------------

class TestHttpHelpers:
    """Tests for low-level HTTP helpers."""

    def test_post_returns_none_on_connection_error(self):
        """_post() returns None when the service is unreachable."""
        with patch.object(mq, "MQ_HTTP_BASE", "http://127.0.0.1:1"):
            result = mq._post("/register", {"agent_id": "test"})
        assert result is None

    def test_get_returns_none_on_connection_error(self):
        """_get() returns None when the service is unreachable."""
        with patch.object(mq, "MQ_HTTP_BASE", "http://127.0.0.1:1"):
            result = mq._get("/status")
        assert result is None

    def test_post_returns_parsed_json_on_success(self):
        """_post() returns parsed JSON on success."""
        body = json.dumps({"status": "registered"}).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("agent_helper.mq.urlopen", return_value=mock_resp):
            result = mq._post("/register", {"agent_id": "test"})

        assert result == {"status": "registered"}


# ---------------------------------------------------------------------------
# register() — with mocked HTTP
# ---------------------------------------------------------------------------

class TestRegister:
    """Tests for register() with mocked HTTP."""

    def test_register_returns_true_on_success(self):
        """register() returns True when HTTP succeeds."""
        with patch.object(mq, "_post", return_value={"status": "ok"}):
            assert mq.register() is True

    def test_register_returns_false_on_failure(self):
        """register() returns False when HTTP fails."""
        with patch.object(mq, "_post", return_value=None):
            assert mq.register() is False

    def test_register_sends_metadata(self):
        """register() posts _AGENT_METADATA to /register."""
        with patch.object(mq, "_post", return_value={"status": "ok"}) as mock_post:
            mq.register()

        mock_post.assert_called_once_with("/register", mq._AGENT_METADATA)


# ---------------------------------------------------------------------------
# _build_message() — message construction
# ---------------------------------------------------------------------------

class TestBuildMessage:
    """Tests for internal message building."""

    def test_build_message_has_required_fields(self):
        """_build_message() returns a dict with all protocol-required fields."""
        msg = mq._build_message(
            to="mail_agent",
            msg_type="info",
            subject="Test subject",
            body="Test body",
        )
        required = {"id", "from", "to", "priority", "type", "subject", "body", "status", "createdAt"}
        for field in required:
            assert field in msg, f"Missing field: {field}"
        assert msg["to"] == "mail_agent"
        assert msg["status"] == "unread"

    def test_build_message_truncates_subject(self):
        """Subject is truncated to 80 characters."""
        long_subject = "x" * 200
        msg = mq._build_message("agent", "info", long_subject, "body")
        assert len(msg["subject"]) <= 80
