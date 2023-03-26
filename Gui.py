"""
Class for instantiating the DBMS GUI.
"""
import tkinter as tk
from Query import Query


class GUI:
    """
    Class for instantiating the DBMS GUI.
    """
    window = None
    query = None
    list_frame = None  # frame holding the list of tables
    data_frame = None  # frame holding a single table of data
    create_frame = None  # frame holding the form to create a new table
    table_list = None    # the tk.Listbox widget which holds the list of tables
    selected = None      # the currently selected table, if applicable

    def __init__(self, query: Query) -> None:
        """
        Class constructor. Initialize tkinter GUI, and the frames that will be used.
        """
        self.window = tk.Tk()
        self.list_frame = tk.Frame(self.window)
        self.list_frame.pack()
        self.data_frame = tk.Frame(self.window)
        self.create_frame = tk.Frame(self.window)

        self.query = query
        self.show_list()  # start off by displaying the list of tables in the database.

        self.window.mainloop()

    def show_list(self):
        """
        Create GUI for showing the list of tables
        """
        lst = self.query.get_table_list()

        # Initialize Listbox widget
        self.table_list = tk.Listbox(self.list_frame, height=10,
                                     width=15,
                                     bg="grey",
                                     activestyle="dotbox",
                                     fg="black")
        tk.Label(self.list_frame, text="TABLES").pack()

        # Index counter
        i = 1

        for table in lst:
            self.table_list.insert(i, table)
            i += 1

        self.table_list.pack()

        # Create buttons and show on screen.
        select_btn = tk.Button(self.list_frame, text="select", command=self._show_table)
        select_btn.pack()

        delete_btn = tk.Button(self.list_frame, text="delete", command=self._delete_table)
        delete_btn.pack()

        create_btn = tk.Button(self.list_frame, text="New", command=self._create_table_ui)
        create_btn.pack()

        return

    def _show_table(self, filter = None):
        """
        Show the selected table.
        """
        # Hide frame containing table list, and show frame containing table data - only when coming from table list.
        if (filter is None):
            self.list_frame.pack_forget()

        # Recreate data_frame to rebuild with data for the selected table.
        self.data_frame.destroy()
        self.data_frame = tk.Frame(self.window)
        self.data_frame.pack()

        if self.data_frame.children == {}:

            # Create frame for holding non-table data widgets.
            upper_frame = tk.Frame(self.data_frame)
            upper_frame.pack(side="top", anchor="nw")

            # Create back button
            back = tk.Button(upper_frame, text="Back", command= lambda: self.return_to_list(self.data_frame))
            back.grid(sticky="w", row = 0, column= 0)

            # Create search label
            tk.Label(upper_frame, text="Filter:").grid(sticky = "e", row =1, column=0)

            # Create search text field and button.
            search = tk.Entry(upper_frame, width=60)
            search.grid(sticky = "w", row = 1, column=1)
            tk.Button(upper_frame, text="go", command=lambda: self._search(search)).grid(row = 1, column=2)

            # Create example label
            tk.Label(upper_frame, text="example: year = 2012 AND make = Toyota").grid(row = 2, column = 1)

            # Create frame for holding all Entry widgets that comprise the table.
            grid_frame = tk.Frame(self.data_frame)
            grid_frame.pack()

            # Identify the selected table
            for i in self.table_list.curselection():
                self.selected = self.table_list.get(i)

            print(self.selected)

            # Get table dimensions and data for iteration
            dim = self.query.get_table_size(self.selected)
            data = self.query.get_table_data(self.selected, filter)

            # When: Rebuild from filtering - keep previous query for ease of changing.
            if filter is not None:
                search.insert(-1, filter)

            # data[0] is a list of the column headers - begin grid GUI by displaying table column headers
            for i in range(len(data[0])):
                e = tk.Entry(grid_frame, width=20, background="grey")
                e.grid(row=1, column=i)
                e.insert(-1, data[0][i])

            # data[1] is the actual table data stored as a 2D list
            data = data[1]

            # Iterate over 2D list, create tk.Entry with data in it to represent a cell of the table
            for i in range(0, dim[0]):
                for j in range(dim[1]):
                    cell = str(data[i][j])
                    e = tk.Entry(grid_frame, width=20)
                    e.grid(row=i + 2, column=j)
                    e.insert(-1, cell)

            # Create buttons for additional functionality
            tk.Button(self.data_frame, text="new row", command=self._new_row).pack()
            tk.Button(self.data_frame, text="save changes", command=self._update_table).pack(side='bottom')

    def _search(self, entry: tk.Entry):
        """
        Execute a simple query on a single table.
        """
        query = entry.get()
        print(query)

        # Empty search field - reset table
        if (query == ''):
            query = None

        try:
            self._show_table(query)

        # avoid error, but works without issue
        except Exception as e:
            print("error:", e)


    def _new_row(self):
        """
        Create a new row in the selected table.
        """
        # Get access to nested frame which holds the table data
        gridFrame = self.data_frame.children["!frame2"]
        widgets = list(gridFrame.children.values())

        # Get grid info about the last widget in the grid (i.e., the last cell in the table)
        info = widgets[-1].grid_info()
        row = info["row"]  
        col = info["column"]
        
        # add new row at index (dim[0] - 1) + 1 -> dim[0] = number of rows in gridFrame
        for i in range(col + 1):
            tk.Entry(gridFrame, width=20).grid(row=row + 1, column=i)


    def _update_table(self):
        """
        Call helper functions to update the table in the database, after which it makes a call to reload the GUI
        """
        # Check if any new rows have been inserted - address if applicable.
        self._check_insert()

        table_data = self.query.get_table_data(self.selected)[1]
        # Check if any rows have been altered - address if applicable.
        self._check_update(table_data)

        # reload table after updates have been applied.
        self._show_table()
        


    def _check_update(self, db_data):
        """
        Update the table in the database where GUI table entries have been changed.
        """
        gridFrame = self.data_frame.children["!frame2"]
        
        widgets = list(gridFrame.children.values())

        # Determine row,col grid index of the LAST widget in the frame
        info = widgets[-1].grid_info()
        row = info["row"]
        col = info["column"]

        table_data = []

        # Omit row 0 b/c it contains the column headers - get GUI table data
        for i in range(1, row):
            temp = []
            for j in range(col + 1):
                index = i * (col+1) + j
                temp.append(widgets[index].get())
            table_data.append(temp)

        not_equal = {}

        # Compare db table with GUI table cell by cell; store altered cells in not_equal
        for i in range(len(table_data)):
            try:
                for j in range(len(table_data[0])):
                    if not (str(db_data[i][j]) == table_data[i][j]):
                        not_equal[(i, j)] = table_data[i][j]
            except IndexError:
                print(f"Error at i = {i}, j = {j}")
            
        print("not equal:", not_equal)

        # structure of 'updates': {pk_value, [{col_1: new_value}, {col_2: new_value}, ...], ...}
        updates = {}
        columns = self.query.get_table_data(self.selected)[0]
        pk = self.query.get_pk(self.selected)
        pk_index = columns.index(pk)  # get index of column that is the primary key

        # Create 'updates' dict by associating primary keys with their respective row updates.
        for cell in not_equal.keys():
            
            pk_value = db_data[cell[0]][pk_index]  # the value of the primary for the given row,col index

            # set value as dict containing update information: column_name = new_value
            if pk_value not in updates:
                updates[pk_value] = dict({columns[cell[1]]: not_equal[cell]})

            # add new {column_name: new_value} key-value pair to the respective row (identified by pk_value)
            else:
                updates[pk_value][columns[cell[1]]] = not_equal[cell]

        print("updates:", updates)

        for pk_value in updates:

            delete = False

            #  Delete rows by clear all fields in it.
            if list(updates[pk_value].values()) == ['' for _ in range(len(updates[pk_value]))]:
                delete = True

            # At least one value in the row is still the same - update instead of delete.
            if not delete:
                self.query.update_row(self.selected, pk, pk_value, updates[pk_value])

            else:
                self.query.delete_row(self.selected, pk, pk_value)

    def _check_insert(self):
        """
        Check for any new rows that are to be inserted.
        """
        # Get the db table size
        db_row, db_col = self.query.get_table_size(self.selected)

        gridFrame = self.data_frame.children["!frame2"]
        widgets = list(gridFrame.children.values())

        info = widgets[-1].grid_info()
        print(widgets[-1].get())

        # Get bottom-most row/col index
        tbl_row = info["row"]
        tbl_col = info["column"]
        print("row:", tbl_row)
        print("col:", tbl_col)

        print(f"{tbl_col} == {db_col - 1}: {tbl_col == db_col - 1}")

        table_data = []

        # Omit row 0 b/c it contains the column headers - get table data
        for i in range(1, tbl_row):
            temp = []
            for j in range(tbl_col + 1):
                index = i * (tbl_col+1) + j
                # print("index", index)
                temp.append(widgets[index].get())
            table_data.append(temp)

        # Compare GUI row count with db row count - attempt to insert new records if GUI row count > db row count
        if tbl_row - 1 > db_row:
            print("checking for newly inserted data")
            new_rows =  tbl_row - 1 - db_row
            print("easy new rows:", new_rows)

            start_index = db_col + db_row * db_col  # calculate first new index

            to_insert = []

            for i in range(new_rows):
                new_values = []
                for j in range(db_col):
                    offset = i * db_col + j  # calculate index offset from start_index
                    new_values.append(widgets[start_index + offset].get())

                to_insert.append(new_values)

            print(to_insert)
            headers = list(self.query.get_table_data(self.selected)[0])
            try:
                to_insert.remove(headers)
            except ValueError:
                pass
            print("after removal:",to_insert)

            for new_row in to_insert:
                self.query.insert_row(self.selected, new_row)
        

    def return_to_list(self, frame, isGrid = False):
        """
        Hide frame and return to list (reveal it).
        """

        if isGrid:
            frame.grid_forget()
        else:
            frame.pack_forget()

        self.list_frame.pack()


    def _delete_table(self):
        """
        Delete from the database the table matching self.selected
        """
        # Get name of selected table.
        for i in self.table_list.curselection():
            self.selected = self.table_list.get(i)

        # Get index of selected table and remove it from the Listbox (GUI)
        slct_index = self.table_list.get(0, tk.END).index(self.selected)
        self.table_list.delete(slct_index)

        # Remove the table from the database
        self.query.delete_table(self.selected)


    def _create_table_ui(self, show = True):
        """Build the UI components for creating a table."""
        # hide table list
        self.list_frame.pack_forget()

        if self.create_frame.children == {}:

            tblNameFrame = tk.Frame(self.create_frame)
            tblNameFrame.pack()

            tk.Button(tblNameFrame, text="back", command= lambda: self.return_to_list(self.create_frame)).grid(sticky = "w", row = 0, column=0)
            tk.Label(tblNameFrame, text="Table Name: ").grid(row = 1, column=0)
            name = tk.Entry(tblNameFrame, width=30)
            name.grid(row=1, column=1)
            
            # Set up headers
            tk.Label(tblNameFrame, text="Attribute name").grid( row = 3, column=0)
            tk.Label(tblNameFrame, text="Attribute type").grid( row = 3, column=1)
            tk.Label(tblNameFrame, text="Attribute constraint(s)").grid( row = 3, column=2)

            # Set up attributeFrame, which holds text fields for attribute details
            attributeFrame = tk.Frame(self.create_frame)
            attributeFrame.pack()

            tk.Entry(attributeFrame, width=30).grid(row=0, column=0)
            tk.Entry(attributeFrame, width=30).grid(row=0, column=1)
            tk.Entry(attributeFrame, width=30).grid(row=0, column=2)

            tk.Button(self.create_frame, text="new attribute", command=self._new_attribute).pack()  # button for adding a new attribute
            tk.Button(self.create_frame, text="create", command=self._create_table).pack()

        # Reveal only if calling from the table list frame
        if show:
            self.create_frame.pack()

    def _new_attribute(self):
        """
        Helper function. Add a new row of Entry() objects to attributeFrame.
        """
        attributeFrame = self.create_frame.children["!frame2"]
        rows = len(attributeFrame.children) // 3

        # add new row at index (rows - 1) + 1
        tk.Entry(attributeFrame, width=30).grid(row=rows, column=0)
        tk.Entry(attributeFrame, width=30).grid(row=rows, column=1)
        tk.Entry(attributeFrame, width=30).grid(row=rows, column=2)
        btn = tk.Button(attributeFrame, text="X", command= lambda: self._del_attribute(btn))
        btn.grid(row=rows, column=3)

        print(btn.grid_info())



    def _del_attribute(self, btn):
        """
        Helper function. On button press, remove a "new attribute" row when creating a table.

        Currently has index issues.
        """
        attributeFrame = self.create_frame.children["!frame2"]
        
        info = btn.grid_info()
        row = info["row"]

        print("delete row: ", row)

        start_index = ((row - 1) * 4) + 3  # row will never be 0 because you can't delete the 0th row in the "table"
        widgets = list(attributeFrame.children.values())

        print(widgets[start_index])

        # Destroy all widgets in the given row
        for i in range(4):
            # Use start_index like a row pointer in C
            widgets[start_index + i].destroy()

    def _create_table(self):
        """
        Helper function. Read data from Entry() objects and parse to create table in database.
        After attempt (may or may not be successful), will return to table list.
        """
        attributeFrame = self.create_frame.children["!frame2"]
        fieldType = 1
        attributes = []  # a 2D list of attribute definitions - each inner list contains details about a single attribute
        attribute = []   # inner list for 2D list 'attributes'

        # Loop over widgets in attributeFrame - repeats a pattern of 3 Entry and 1 Button
        for field in attributeFrame.children.values():

            if not isinstance(field, tk.Button):
                # Attribute name
                if fieldType == 1:
                    print("attribute name")
                    attribute.append(field.get())
                    fieldType += 1

                # Attribute type
                elif fieldType == 2:
                    print("attribute type")
                    attribute.append(field.get())
                    fieldType += 1

                # Attribute constraints (e.g., primary key, unique, not null)
                else:
                    print("attribute constraints")
                    attribute.append(field.get())
                    attributes.append(attribute)
                    attribute = []  # reached a new "row" and thus a new "attribute" - reset
                    fieldType = 1

                print(field.get())

        # get table name from create_frame -> tblNameFrame -> Entry().get()
        table_name = self.create_frame.children["!frame"].children['!entry'].get()
        print(table_name)
        print(attributes)

        try:
            # Attempt to execute SQL command to create a new table with the given parameters
            self.query.create_table(table_name, attributes)
            self.table_list.insert(self.table_list.size(), table_name)  # insert at index (n - 1) + 1
            self._reset_create_frame()  # clear form for later use
            
        except Exception as e:
            print(e)

        # Return to the table list
        self.return_to_list(self.create_frame)

    def _reset_create_frame(self):
        """
        Helper function. Reset create_frame upon successful table creation.
        """
        print("_reset_create_frame()")

        # Destroy the create_frame so that it may be recreated - for resetting fields
        self.create_frame.destroy()
        self.create_frame = tk.Frame(self.window)

        # recreate frame without showing it to the screen
        self._create_table_ui(show=False)






        

        


