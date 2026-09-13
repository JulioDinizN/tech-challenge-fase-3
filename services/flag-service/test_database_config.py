import unittest

from database_config import build_database_config


class DatabaseConfigTest(unittest.TestCase):
    def test_database_url_has_priority(self):
        self.assertEqual(
            build_database_config(
                {"DATABASE_URL": "postgres://local:local@db:5432/flags_db"}
            ),
            {"dsn": "postgres://local:local@db:5432/flags_db"},
        )

    def test_split_settings_keep_password_separate(self):
        config = build_database_config(
            {
                "DB_HOST": "flags.postgresql.internal",
                "DB_PORT": "5433",
                "DB_NAME": "flags_db",
                "DB_USER": "flags_app",
                "DB_PASSWORD": "p@ss:/?# word",  # nosec B105
                "DB_SSLMODE": "verify-full",
            }
        )
        self.assertEqual(config["password"], "p@ss:/?# word")
        self.assertEqual(config["port"], 5433)
        self.assertEqual(config["sslmode"], "verify-full")
        self.assertNotIn("dsn", config)

    def test_missing_setting_is_rejected_without_leaking_password(self):
        with self.assertRaisesRegex(ValueError, "DB_NAME") as context:
            build_database_config(
                {
                    "DB_HOST": "postgres",
                    "DB_USER": "flags_app",
                    "DB_PASSWORD": "do-not-leak",  # nosec B105
                }
            )
        self.assertNotIn("do-not-leak", str(context.exception))


if __name__ == "__main__":
    unittest.main()
