"""
Class used to query the MySQL database.
"""
from Connect import Connect


class Query:
    """Collection of functions which return the results of SQL query commands."""
    connect = None
    cursor = None  # object used to execute SQL commands.

    def __init__(self, connection: Connect):
        self.connect = connection
        self.cursor = connection.cursor

    def get_table_list(self) -> list:
        """
        Return the list of tables in teh database.
        """
        self.cursor.execute("SHOW FULL tables WHERE Table_Type != 'VIEW'")

        temp = self.cursor.fetchall()


        return [name[0] for name in temp]

    def get_table_size(self, table_name: str):
        """
        Return the size of the given table
        """
        self.cursor.execute(f"SELECT * FROM {table_name}")
        self.cursor.fetchall()  # call to clear buffer

        return (self.cursor.rowcount, len(self.cursor.column_names))

    def delete_table(self, table_name: str):
        """
        Delete table_name from the database.
        """
        self.cursor.execute(f"DROP TABLE {table_name}")

    def get_table_data(self, table_name, filter = None):
        """
        Return the query result of

                SELECT * FROM table_name

        as a tuple, where the first element is the table column names, and the second element is the table row data.
        """
        if filter is None:
            self.cursor.execute(f"SELECT * FROM {table_name}")

        else:
            split = filter.split(" ")
            print(split)
            for i in range(len(split)):
                if split[i] == "=":
                    split[i + 1] = f"'{split[i + 1]}'"

            print(split)
            filter = ' '.join(split)

            sql = f"SELECT * FROM {table_name} WHERE {filter}"
            print(sql)

            self.cursor.execute(sql)
        
        return (self.cursor.column_names, self.cursor.fetchall())
    
    def create_table(self, table_name: str, attributes: list):
        """
        Execute an SQL command to create a new table in the database.
        """
        # sql: variable used to build SQL command with the given inputs.
        sql = f"CREATE TABLE {table_name} ("

        for attr in attributes:
            sql = sql + f"{attr[0]} {attr[1]} {attr[2]}"
            
            if attr != attributes[-1]:
                sql += ", "

            print(sql)
        sql += ")"

        print(f"final: {sql}")

        self.cursor.execute(sql)

    def filter_table(self, table_name, filter: str):
        """
        Return the result of executing an SQL simply query (on a single table).
        """
        

        print(self.cursor.column_names, self.cursor.fetchall())

    def get_pk(self, table_name):
        """
        Return the name of the primary key of table_name.
        """
        self.cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")

        return self.cursor.fetchall()[0][4]
    
    def update_row(self, table_name, pk_name, pk_value, update: dict[str: str]):
        """
        Execute SQL's UPDATE statement on the given row (WHERE 'primary_key = 'value')

        Parameters:
            - update: a dictionary whose entries store column_name:new_value pairs that need updating.
        """
        sql = f"UPDATE {table_name} SET "

        # Get the last updated column to help build sql string
        last = list(update)[-1]

        for col in update:
            # updates is of the form: {column_name: new_value}, so col = column_name
            sql += f"{col} = '{update[col]}'"

            if col != last:
                sql += ", "
        
        # Set condition to identify the given row.
        sql += f" WHERE {pk_name} = {pk_value}"

        print(sql)

        # Execute SQL command
        self.cursor.execute(sql)

        # Call fetchall() to clear buffer
        self.cursor.fetchall()

    def insert_row(self, table_name, row: list):
        """
        Insert values into table with name 'table_name'.

        'row' must be a list with values matching in type and order to table.
        """
        # Only execute if all values are inserted.
        if '' not in row:
            sql = f"INSERT INTO {table_name} VALUES ("

            for value in row:
                sql += f"'{value}'"

                if value != row[-1]:
                    sql += ", "

            sql += ")"

            print(sql)

            self.cursor.execute(sql)
            self.cursor.fetchall()

    def delete_row(self, table_name: str, pk_name, pk_value):
        """
        Delete the record corresponding to the given primary key value 'pk_value'.
        """
        sql = f"DELETE FROM {table_name} WHERE {pk_name} = {pk_value}"
        print(sql)
        self.cursor.execute(sql)
        self.cursor.fetchall()  # clear cursor buffer






