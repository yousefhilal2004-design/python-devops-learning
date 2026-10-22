import unittest

from part21.status_checker import classify_http_status


class TestClassifyHttpStatus(unittest.TestCase):

    def test_success_status(self):
        self.assertEqual(classify_http_status(200), "success")
        self.assertEqual(classify_http_status(201), "success")
        self.assertEqual(classify_http_status(299), "success")

    def test_redirect_status(self):
        self.assertEqual(classify_http_status(301), "redirect")
        self.assertEqual(classify_http_status(399), "redirect")

    def test_client_error_status(self):
        self.assertEqual(classify_http_status(400), "client_error")
        self.assertEqual(classify_http_status(404), "client_error")
        self.assertEqual(classify_http_status(499), "client_error")

    def test_server_error_status(self):
        self.assertEqual(classify_http_status(500), "server_error")
        self.assertEqual(classify_http_status(503), "server_error")
        self.assertEqual(classify_http_status(599), "server_error")

    def test_informational_status(self):
        self.assertEqual(classify_http_status(100), "informational")
        self.assertEqual(classify_http_status(199), "informational")

    def test_invalid_low_status(self):
        with self.assertRaises(ValueError):
            classify_http_status(99)

    def test_invalid_high_status(self):
        with self.assertRaises(ValueError):
            classify_http_status(600)

    def test_string_is_rejected(self):
        with self.assertRaises(TypeError):
            classify_http_status("200")

    def test_boolean_is_rejected(self):
        with self.assertRaises(TypeError):
            classify_http_status(True)


if __name__ == "__main__":
    unittest.main()
