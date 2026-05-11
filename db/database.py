"""
Singleton Pattern — Database Connection Manager
SE-211 Lab 14: Personal Finance Management System

Design Pattern : Singleton
Purpose        : Ensures only ONE MySQL connection instance exists
                 throughout the entire application lifecycle.
                 Every module that calls DatabaseConnection() gets
                 the same shared instance — no duplicate connections.
"""

import mysql.connector
from mysql.connector import Error


# ──────────────────────────────────────────────────────────
#  ⚙️  CHANGE THESE TO MATCH YOUR MYSQL WORKBENCH SETTINGS
# ──────────────────────────────────────────────────────────
DB_HOST     = "localhost"   # Workbench hostname (usually localhost)
DB_USER     = "root"        # Workbench username
DB_PASSWORD = "alij"            # ← paste your Workbench password here
DB_NAME     = "finance_db"  # Database name you created in Workbench
DB_PORT     = 3306          # Default MySQL port
# ──────────────────────────────────────────────────────────


class DatabaseConnection:
    """
    Singleton class to manage a single MySQL database connection
    throughout the application lifecycle.

    Usage:
        db = DatabaseConnection()          # returns same instance every time
        conn = db.get_connection()         # get raw MySQL connection
        cursor = db.execute("SELECT ...") # run a query directly
    """

    _instance = None  # Holds the one and only instance

    def __new__(cls):
        """
        Called every time DatabaseConnection() is used.
        Only creates a new instance if one doesn't exist yet.
        """
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._connection = None
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        """Establish the MySQL connection using the credentials above."""
        try:
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT,
                autocommit=True
            )
            print("✅ MySQL connection established (Singleton instance).")
            print(f"   Connected to: {DB_HOST}:{DB_PORT} / {DB_NAME}")

        except Error as e:
            print(f"⚠️  MySQL not available: {e}")
            print("   Running in in-memory mode (sample data only).")
            self._connection = None

    def get_connection(self):
        """
        Returns the active MySQL connection.
        Reconnects automatically if the connection was dropped.
        """
        if self._connection and self._connection.is_connected():
            return self._connection
        # Connection lost — try to reconnect
        print("🔄 Reconnecting to MySQL...")
        self._connect()
        return self._connection

    def execute(self, query, params=None):
        """
        Execute a SQL query and return the cursor.

        Args:
            query  : SQL string e.g. "SELECT * FROM transactions WHERE user_id = %s"
            params : tuple of values e.g. (1,)

        Returns:
            cursor (dictionary=True so rows come back as dicts), or None if no connection.

        Example:
            cursor = db.execute("SELECT * FROM goals WHERE user_id = %s", (1,))
            rows = cursor.fetchall()
        """
        conn = self.get_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor

    def execute_many(self, query, params_list):
        """
        Execute a SQL query multiple times with different parameters.
        Useful for bulk inserts.

        Args:
            query       : SQL string with %s placeholders
            params_list : list of tuples

        Example:
            db.execute_many(
                "INSERT INTO transactions (user_id, description, amount) VALUES (%s, %s, %s)",
                [(1, 'Salary', 85000), (1, 'KFC', 1200)]
            )
        """
        conn = self.get_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        return cursor

    def is_connected(self):
        """Returns True if the database connection is active."""
        return self._connection is not None and self._connection.is_connected()

    def close(self):
        """Close the connection and reset the Singleton instance."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            DatabaseConnection._instance = None
            print("🔒 MySQL connection closed.")


# ──────────────────────────────────────────────────────────
# Quick connection test — run this file directly to verify:
#   python db/database.py
# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()

    print(f"\nSingleton check — same instance? {db1 is db2}")  # Must be True
    print(f"Connected to MySQL? {db1.is_connected()}")

    if db1.is_connected():
        cursor = db1.execute("SELECT COUNT(*) AS total FROM transactions")
        row = cursor.fetchone()
        print(f"Transactions in DB: {row['total']}")

    db1.close()