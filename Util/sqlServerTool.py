import pyodbc


class SQLServerTool:
    def __init__(self, server, database, username, password):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.conn = None
        self.cursor = None

    def connect(self):
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};SERVER="
            + self.server
            + ";DATABASE="
            + self.database
            + ";UID="
            + self.username
            + ";PWD="
            + self.password
            + ";TrustServerCertificate=yes"
        )
        self.conn = pyodbc.connect(conn_str)
        self.cursor = self.conn.cursor()

    def execute_query(self, query):
        self.cursor.execute(query)

    def fetch_one(self):
        return self.cursor.fetchone()

    def fetch_all(self):
        return self.cursor.fetchall()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
