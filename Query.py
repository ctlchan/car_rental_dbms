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

    def get_table_data(self, table_name):
        """
        Return the query result of

                SELECT * FROM table_name

        as a tuple, where the first element is the table column names, and the second element is the table row data.
        """
        self.cursor.execute(f"SELECT * FROM {table_name}")
        
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

    def filter_table(self, table_name, query: str):
        """
        Return the result of executing an SQL simply query (on a single table).
        """
        # self.cursor.execute
