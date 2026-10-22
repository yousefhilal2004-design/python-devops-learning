import unittest


class TestAssertionsDemo(unittest.TestCase):

    def test_basic_assertions(self):
        self.assertEqual(2 + 3, 5)
        self.assertNotEqual(2 + 3, 6)
        self.assertTrue(10 > 5)
        self.assertFalse(10 < 5)
        self.assertIsNone(None)
        self.assertIn("ERROR", ["INFO", "WARNING", "ERROR"])


if __name__ == "__main__":
    unittest.main()
