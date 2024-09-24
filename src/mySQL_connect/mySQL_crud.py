from typing import Any
import pandas as pd
import mysql.connector
import json
from mysql.connector import Error


class MySQLOperation:
    __connection = None
    __database = None

    def __init__(self, host: str, database_name: str, user: str, password: str):
        self.host = host
        self.database_name = database_name
        self.user = user
        self.password = password

    def create_connection(self):
        try:
            self.__connection = mysql.connector.connect(
                host=self.host,
                database=self.database_name,
                user=self.user,
                password=self.password
            )
            if self.__connection.is_connected():
                return self.__connection
        except Error as e:
            print(f"Error: {e}")
            return None

    def create_database(self):
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database_name}")
        cursor.close()
        connection.close()

    def create_table(self, table_name: str, columns: str):
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        cursor.close()
        connection.close()

    def insert_record(self, table_name: str, record: dict) -> Any:
        connection = self.create_connection()
        cursor = connection.cursor()
        placeholders = ', '.join(['%s'] * len(record))
        columns = ', '.join(record.keys())
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, list(record.values()))
        connection.commit()
        cursor.close()
        connection.close()

    def bulk_insert(self, datafile: str, table_name: str):
        if datafile.endswith('.csv'):
            dataframe = pd.read_csv(datafile, encoding='utf-8')
        elif datafile.endswith('.xlsx'):
            dataframe = pd.read_excel(datafile, encoding='utf-8')

        connection = self.create_connection()
        cursor = connection.cursor()
        for row in dataframe.itertuples(index=False):
            placeholders = ', '.join(['%s'] * len(row))
            sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
            cursor.execute(sql, row)
        connection.commit()
        cursor.close()
        connection.close()
