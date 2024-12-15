import psycopg2

class DatabaseManager:
    def __init__(self, db_name, user, password, host="localhost", port=5432):
        self.connection = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.connection.cursor()

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.fetchall() if self.cursor.description else None
        except Exception as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()

    def close(self):
        self.cursor.close()
        self.connection.close()
