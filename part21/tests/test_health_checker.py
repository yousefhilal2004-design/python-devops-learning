import unittest
from unittest.mock import Mock, patch

import requests

from part21.health_checker import check_endpoint


class TestCheckEndpoint(unittest.TestCase):

    @patch("part21.health_checker.requests.get")
    def test_successful_endpoint(self, mock_get):
        mock_get.return_value = Mock(status_code=200)

        result = check_endpoint("https://example.com")

        self.assertTrue(result["healthy"])
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["message"], "Endpoint is healthy")
        mock_get.assert_called_once_with(
            "https://example.com",
            timeout=5.0,
            allow_redirects=True,
        )

    @patch("part21.health_checker.requests.get")
    def test_redirect_response(self, mock_get):
        mock_get.return_value = Mock(status_code=301)

        result = check_endpoint("https://example.com")

        self.assertTrue(result["healthy"])
        self.assertEqual(result["status_code"], 301)

    @patch("part21.health_checker.requests.get")
    def test_server_error(self, mock_get):
        mock_get.return_value = Mock(status_code=503)

        result = check_endpoint("https://example.com")

        self.assertFalse(result["healthy"])
        self.assertEqual(result["status_code"], 503)

    @patch("part21.health_checker.requests.get")
    def test_timeout(self, mock_get):
        mock_get.side_effect = requests.Timeout()

        result = check_endpoint("https://example.com")

        self.assertFalse(result["healthy"])
        self.assertIsNone(result["status_code"])
        self.assertEqual(result["message"], "Request timed out")

    @patch("part21.health_checker.requests.get")
    def test_connection_error(self, mock_get):
        mock_get.side_effect = requests.ConnectionError()

        result = check_endpoint("https://example.com")

        self.assertFalse(result["healthy"])
        self.assertIsNone(result["status_code"])
        self.assertIn("Request failed", result["message"])

    def test_empty_url_is_rejected(self):
        with self.assertRaises(ValueError):
            check_endpoint("")

    def test_invalid_scheme_is_rejected(self):
        with self.assertRaises(ValueError):
            check_endpoint("ftp://example.com")

    def test_invalid_timeout_is_rejected(self):
        with self.assertRaises(ValueError):
            check_endpoint("https://example.com", timeout=0)

    def test_wrong_timeout_type_is_rejected(self):
        with self.assertRaises(TypeError):
            check_endpoint("https://example.com", timeout="five")


if __name__ == "__main__":
    unittest.main()
