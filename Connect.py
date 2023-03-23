"""
-------------------------------------------------------
Author:  David Brown
ID:      999999999
Email:   dbrown@wlu.ca
__updated__ = "2022-09-30"
-------------------------------------------------------
"""
# pylint: disable=broad-except

# Imports
from configparser import ConfigParser

from mysql.connector import connect, Error


class Connect:
    """
    -------------------------------------------------------
    Provides Python mysql.connector connection to a database.
    Requires option file of the form:

    [database]
    user = ...
    password = ...
    host = hopper.wlu.ca
    database = ...

    Note: does not use connect(option_files=...) syntax
    only because error messages are not specific enough.
    -------------------------------------------------------
    """
    connection = None
    cursor = None

    def __init__(self, option_file, port=None):
        """
        -------------------------------------------------------
        Initialize a MySQL database connection object.
        Use: connection = Connect(option_file)
        -------------------------------------------------------
        Parameters:
            option_file - name of option file (str)
        Returns:
            A database connection object (Connect)
        -------------------------------------------------------
        """
        try:
            # Read the contents of the option file
            config = ConfigParser()
            config.read_file(open(option_file))
            # Extract the database section into a dictionary
            params = dict(config['database'])
            params['raise_on_warnings'] = True
            params['use_unicode'] = True
            params['autocommit'] = True

            if port is not None:
                params['port'] = port
            # Connect to the database
            if self.connection is None:
                self.connection = connect(**params)
                self.cursor = self.connection.cursor()
        except FileNotFoundError:
            raise Exception(
                f"Option file '{option_file}' not found.")
        except KeyError as err:
            if 'database' not in config.sections():
                raise Exception("Option file missing section 'database'.")
            else:
                raise err
        except Error as err:
            if err.sqlstate == '28000':
                raise Exception("Invalid username or password")
            elif err.sqlstate == '42000':
                raise Exception(
                    f"Database '{params['database']}' does not exist")
            else:
                raise err
        except Exception as err:
            print(err)
        return

    def close(self):
        """
        Closes the database connection.
        """
        try:
            self.connection.close()
            self.connection = None
        except AttributeError:
            raise Exception("Database connection is already closed.")
        return
