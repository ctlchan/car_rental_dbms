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
    list_frame = None
    grid_frame = None
    create_frame = None
    table_list = None
    selected = None

    def __init__(self, query) -> None:
        print("__init__()")
        self.window = tk.Tk()
        self.list_frame = tk.Frame(self.window)
        self.list_frame.pack()
        self.grid_frame = tk.Frame(self.window)
        self.create_frame = tk.Frame(self.window)

        self.query = query
        self.show_list()

        self.window.mainloop()

    def show_list(self):
        """
        Create UI for showing the list of tables
        """
        lst = self.query.get_table_list()
        self.table_list = tk.Listbox(self.list_frame, height=10,
                                     width=15,
                                     bg="grey",
                                     activestyle="dotbox",
                                     fg="black")
        tk.Label(self.list_frame, text="TABLES").pack()
        i = 1

        for table in lst:
            self.table_list.insert(i, table)
            i += 1

        self.table_list.pack()

        select_btn = tk.Button(self.list_frame, text="select", command=self._show_table)
        select_btn.pack()

        delete_btn = tk.Button(self.list_frame, text="delete", command=self._delete_table)
        delete_btn.pack()

        create_btn = tk.Button(self.list_frame, text="New", command=self._create_table_ui)
        create_btn.pack()


        return

    def _show_table(self):
        """
        Show the selected table.
        """
        # Hide frame containing table list, and show frame containing table data.
        self.list_frame.pack_forget()
        self.grid_frame.grid()

        back = tk.Button(self.grid_frame, text="Back", command= lambda: self.return_to_list(self.grid_frame, True))
        back.grid(sticky = "w", row = 0, column=0)

        for i in self.table_list.curselection():
            self.selected = self.table_list.get(i)

        print(self.selected)

        dim = self.query.get_table_size(self.selected)
        data = self.query.get_table_data(self.selected)

        for i in range(len(data[0])):
            
            e = tk.Entry(self.grid_frame, width=20, background="grey")
            e.grid(row=1, column=i)
            e.insert(-1, data[0][i])

        data = data[1]

        for i in range(0, dim[0]):
            for j in range(dim[1]):
                cell = str(data[i][j])
                e = tk.Entry(self.grid_frame, width=20)
                e.grid(row=i + 2, column=j)
                e.insert(-1, cell)


    def return_to_list(self, frame, isGrid = False):
        """
        Hide frame and return to list.
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

        for i in self.table_list.curselection():
            self.selected = self.table_list.get(i)


        slct_index = self.table_list.get(0, tk.END).index(self.selected)
        self.table_list.delete(slct_index)
        
        # TODO: call delete query!!


        # for widget in self.frame.winfo_children():
        #     widget.pack_forget()
        # self.show_list()

    def _create_table_ui(self):
        """Create a new table in the database."""
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

            attributeFrame = tk.Frame(self.create_frame)
            attributeFrame.pack()

            tk.Entry(attributeFrame, width=30).grid(row=0, column=0)
            tk.Entry(attributeFrame, width=30).grid(row=0, column=1)
            tk.Entry(attributeFrame, width=30).grid(row=0, column=2)

            tk.Button(self.create_frame, text="new attribute", command=self._new_attribute).pack()  # button for adding a new attribute
            tk.Button(self.create_frame, text="create", command=self._create_table).pack()


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

    def _create_table(self):
        """
        Helper function. Read data from Entry() objects and parse to create table in database.
        After attempt (may or may not be successful), will return to table list.
        """
        attributeFrame = self.create_frame.children["!frame2"]
        fieldType = 1
        attributes = []
        attribute = []

        for field in attributeFrame.children.values():

            if fieldType == 1:
                print("attribute name")
                attribute.append(field.get())
                fieldType += 1
            elif fieldType == 2:
                print("attribute type")
                attribute.append(field.get())
                fieldType += 1
            else:
                print("attribute constraints")
                attribute.append(field.get())

                attributes.append(attribute)
                attribute = []
                fieldType = 1
            print(field.get())

        # get table name from create_frame -> tblNameFrame -> Entry().get()
        table_name = self.create_frame.children["!frame"].children['!entry'].get()
        print(table_name)


        print(attributes)
        self.query.create_table(table_name, attributes)


        

        


