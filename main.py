from Connect import Connect
from Tunnel import Tunnel
from Gui import GUI
from Query import Query

# Constants - connection definition files
DCRIS_FILE = "options_file.txt"
HOPPER_FILE = "hopper.txt"

if __name__ == "__main__":

    # Connect to the DCRIS database with an option file
    try:
        # Following 3 lines used when running on the SCHOOL database.
        # tunnel = Tunnel(HOPPER_FILE)
        # with tunnel.tunnel:
            # conn = Connect(DCRIS_FILE)
            conn = Connect("local.txt")  # local.txt follows the same format as DCRIS_FILE but contains information to connect to the local root database instead.
            query = Query(conn)
            gui = GUI(query)
    
    except Exception as e:
        print(str(e))

    print("Program end")
