from datetime import datetime
import sys
import mysql.connector
import os
import json

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


class STVClient:
    def __init__(self, schema: dict, database_name: str, table_name: str):
        try:
            with open(os.path.join(PROJECT_DIR, "config.json")) as f:
                CONFIG = json.load(f)
                SQL_USER = CONFIG["mysql_user"]
                SQL_PASSWORD = CONFIG["mysql_password"]
                assert isinstance(SQL_USER, str)
                assert isinstance(SQL_PASSWORD, str)
        except (AssertionError, KeyError) as e:
            raise Exception(f"Unable to load config.json: {e}")

        self.schema = schema
        self.database_name = database_name
        self.table_name = table_name

        self.__validate_schema_format()

        self.connection: mysql.connector.MySQLConnection = mysql.connector.connect(
            host="esm-mysql-public-do-user-7320955-0.b.db.ondigitalocean.com",
            port=25060,
            user=SQL_USER,
            password=SQL_PASSWORD,
            database=database_name,
        )
        if not self.__table_exists():
            self.__create_table()
        elif not self.__table_schemas_match():
            self.__drop_table()
            self.__create_table()

    def __validate_schema_format(self):
        """
        Checks, whether the given schema is valid.
        """
        reserved_keys = ["id", "date", "hour"]
        allowed_types = ["string", "float"]
        allowed_ascii_values = (
            [ord("_")]
            + list(range(ord("a"), ord("z") + 1))
            + list(range(ord("0"), ord("9") + 1))
        )
        try:
            for key, data_type in self.schema.items():
                assert isinstance(key, str), "key has to be a string"
                assert all(
                    [ord(c) in allowed_ascii_values for c in key]
                ), "only lowercase letters, underscores and numbers allowed in keys"
                assert key not in reserved_keys, "the keys {reserved_keys} are reserved"
                assert data_type in allowed_types, f"allowed datatypes: {allowed_types}"
        except AssertionError as e:
            raise Exception(f"Invalid schema: {e}")

    def __validate_data_format(self, data: dict):
        """
        Checks, whether the data is in the correct format with respect to the
        given schema.
        """
        try:
            assert isinstance(data, dict), "pass data in dict format"
            assert sorted(data.keys()) == sorted(
                self.schema.keys()
            ), "data.keys != schema.keys"

            for key, data_type in self.schema.items():
                if data_type == "string":
                    assert isinstance(data[key], str), f"type(data[{key}]) != string"
                    assert len(data[key]) < 32, "len(data[{key}]) >= 31 characters"
                else:
                    assert isinstance(
                        data[key], int | float
                    ), f"type(data[{key}]) != number"
        except AssertionError as e:
            raise Exception(f"Invalid data format: {e}")

    def __drop_table(self):
        if input("drop the existing table? (y) ").startswith("y"):
            cursor = self.connection.cursor()
            cursor.execute(f"DROP TABLE {self.table_name}", ())
            self.connection.commit()
            print(f"table {self.table_name} dropped")
        else:
            raise Exception("schema has changed, table has to be dropped")

    def __create_table(self):
        """
        Creates the required table based on the give schema.
        """
        cursor = self.connection.cursor()
        sql_types = {"string": "VARCHAR(32)", "float": "FLOAT", "int": "INT"}
        columns = [f"{key} {sql_types[value]}" for key, value in self.schema.items()]
        sql_statement = (
            f"CREATE TABLE {self.table_name} ("
            + "ID INT NOT NULL AUTO_INCREMENT, "
            + "date INT NOT NULL, "
            + "hour FLOAT NOT NULL, "
            + f"{' ,'.join(columns)}"
            + ", PRIMARY KEY (ID));"
        )
        cursor.execute(sql_statement, ())
        self.connection.commit()
        print(f"table {self.table_name} created: {sql_statement}")

    def __table_exists(self):
        """
        Checks, whether the respective table exists.
        """
        cursor = self.connection.cursor()
        cursor.execute("SHOW TABLES", ())
        return self.table_name in [r[0] for r in cursor.fetchall()]

    def __table_schemas_match(self):
        """
        Checks, whether the respective table has the correct columns.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DESCRIBE {self.database_name}.{self.table_name}")
            columns = cursor.fetchall()
            assert columns[0] == ("ID", b"int", "NO", "PRI", None, "auto_increment")
            assert columns[1][:3] == ("date", b"int", "NO")
            assert columns[2][:3] == ("hour", b"float", "NO")
            assert len(columns) == 3 + len(self.schema.items())
            _i = 3
            for key, datatype in self.schema.items():
                assert columns[_i][0] == key
                assert (
                    columns[_i][1].decode().replace("varchar(32)", "string") == datatype
                )
                _i += 1
            return True
        except AssertionError:
            return False

    def insert_data(self, data: dict):
        self.__validate_data_format(data)
        now = datetime.now()
        date = now.strftime("%Y%m%d")
        hour = round(
            (
                now.hour
                + (now.minute / 60.0)
                + (now.second / 3600.0)
                + (now.microsecond / (3_600_000_000.0))
            ),
            6,
        )

        try:
            cursor = self.connection.cursor()
            keys = data.keys()
            values = [str(data[key]) for key in keys]
            sql_statement = (
                f"INSERT INTO {self.table_name} "
                + f"(date, hour, {', '.join(keys)})"
                + " VALUES "
                + f"({date}, {hour}, {', '.join(['%s']*len(keys))})"
            )
            print(
                f"SQL statement: \"{sql_statement.replace('%s', '{}').format(*values)}\""
            )
            cursor.execute(sql_statement, values)
            self.connection.commit()
            assert cursor.rowcount == 1, "Row could not be inserted - reason unknown"
        except Exception as e:
            raise Exception(f"Error when performing insert: {e}")

    def get_latest_n_records(self, n: int):
        cursor = self.connection.cursor()
        cursor.execute(
            f"SELECT * FROM {self.table_name} ORDER BY ID DESC LIMIT {n}", ()
        )
        return cursor.fetchall()

    def execute_sql_statement(self, sql_statement: str):
        cursor = self.connection.cursor()
        cursor.execute(sql_statement, ())
        return cursor.fetchall()

    def __del__(self):
        try:
            self.connection.close()
        except:
            pass
        del self
