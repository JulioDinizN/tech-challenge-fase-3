import unittest

from database_config import build_database_config


class DatabaseConfigTest(unittest.TestCase):
    def test_database_url_has_priority(self):
        self.assertEqual(
            build_database_config(
                {"DATABASE_URL": "postgres://local:local@db:5432/targeting_db"}
            ),
            {"dsn": "postgres://local:local@db:5432/targeting_db"},
        )

    def test_split_settings_keep_password_separate(self):
        config = build_database_config(
            {
                "DB_HOST": "targeting.postgresql.internal",
                "DB_NAME": "targeting_db",
                "DB_USER": "targeting_app",
                "DB_PASSWORD": "p@ss:/?# word",  # nosec B105
            }
        )
        self.assertEqual(config["password"], "p@ss:/?# word")
        self.assertEqual(config["port"], 5432)
        self.assertEqual(config["sslmode"], "require")
        self.assertNotIn("dsn", config)

    def test_invalid_port_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "DB_PORT"):
            build_database_config(
                {
                    "DB_HOST": "postgres",
                    "DB_PORT": "not-a-number",
                    "DB_NAME": "targeting_db",
                    "DB_USER": "targeting_app",
                    "DB_PASSWORD": "do-not-leak",  # nosec B105
                }
            )


if __name__ == "__main__":
    unittest.main()
