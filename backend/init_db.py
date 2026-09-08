import time

from app import get_db_connection


def initialize_database():
    max_attempts = 10

    for attempt in range(1, max_attempts + 1):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(255),
                    description TEXT,
                    file_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            connection.commit()

            cursor.close()
            connection.close()

            print("Database initialization completed successfully.")
            return

        except Exception as error:
            print(
                f"Database initialization attempt "
                f"{attempt}/{max_attempts} failed: {error}"
            )

            if attempt == max_attempts:
                raise

            time.sleep(10)


if __name__ == "__main__":
    initialize_database()
