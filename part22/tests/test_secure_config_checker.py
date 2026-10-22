import unittest

from part22.secure_config_checker import check_configuration


class TestSecureConfiguration(unittest.TestCase):

    def test_valid_development_configuration(self):
        env = {
            "APP_ENV": "development",
            "API_KEY": "local-test-key-123",
        }

        self.assertEqual(check_configuration(env), [])

    def test_valid_production_environment_name(self):
        env = {
            "APP_ENV": "production",
            "API_KEY": "test-value-not-a-real-credential",
        }

        self.assertEqual(check_configuration(env), [])

    def test_missing_app_environment(self):
        env = {
            "API_KEY": "local-test-key-123",
        }

        errors = check_configuration(env)

        self.assertIn("APP_ENV is missing", errors)

    def test_missing_api_key(self):
        env = {
            "APP_ENV": "development",
        }

        errors = check_configuration(env)

        self.assertIn("API_KEY is missing", errors)

    def test_unsupported_environment(self):
        env = {
            "APP_ENV": "prodution",
            "API_KEY": "local-test-key-123",
        }

        errors = check_configuration(env)

        self.assertIn("APP_ENV has an unsupported value", errors)

    def test_placeholder_api_key(self):
        env = {
            "APP_ENV": "development",
            "API_KEY": "replace-me",
        }

        errors = check_configuration(env)

        self.assertIn(
            "API_KEY still contains a placeholder value",
            errors,
        )

    def test_empty_configuration(self):
        errors = check_configuration({})

        self.assertIn("APP_ENV is missing", errors)
        self.assertIn("API_KEY is missing", errors)

    def test_secret_value_is_not_in_error_messages(self):
        secret = "test-secret-do-not-print"
        env = {
            "APP_ENV": "development",
            "API_KEY": "",
        }

        errors = check_configuration(env)
        combined_errors = " ".join(errors)

        self.assertNotIn(secret, combined_errors)

    def test_environment_name_is_case_insensitive(self):
        env = {
            "APP_ENV": "DEVELOPMENT",
            "API_KEY": "local-test-key-123",
        }

        self.assertEqual(check_configuration(env), [])


if __name__ == "__main__":
    unittest.main()
