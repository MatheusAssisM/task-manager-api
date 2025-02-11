import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_smtp_server():
    mock = Mock()
    mock.__enter__ = Mock(return_value=mock)
    mock.__exit__ = Mock(return_value=None)
    return mock


@pytest.fixture
def smtp_config():
    return {
        "SMTP_HOST": "smtp.test.com",
        "SMTP_PORT": "587",  # As string since os.getenv returns strings
        "SMTP_USER": "test_user",
        "SMTP_PASSWORD": "test_pass",
        "SMTP_FROM_EMAIL": "from@test.com",
    }


def mock_getenv(key, default=None):
    config = {
        "SMTP_HOST": "smtp.test.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "test_user",
        "SMTP_PASSWORD": "test_pass",
        "SMTP_FROM_EMAIL": "from@test.com",
    }
    return config.get(key, default)


def mock_getenv_no_auth(key, default=None):
    config = {
        "SMTP_HOST": "smtp.test.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "",
        "SMTP_PASSWORD": "",
        "SMTP_FROM_EMAIL": "from@test.com",
    }
    return config.get(key, default)


def test_send_email_smtp_error(mock_smtp_server):
    with patch("smtplib.SMTP") as mock_smtp_class, patch(
        "os.getenv", side_effect=mock_getenv
    ):
        # Set up SMTP mock
        mock_smtp_class.return_value = mock_smtp_server
        mock_smtp_server.send_message.side_effect = Exception("SMTP Error")

        from src.services.email import EmailService

        email_service = EmailService()

        # Act & Assert
        with pytest.raises(Exception, match="SMTP Error"):
            email_service.send_email(
                to_email="test@example.com", subject="Test Subject", body="Test Body"
            )
