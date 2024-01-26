import socket
import sys
import os
import struct

ROOT_DIRECTORY = "CLIENT_DATA"

TCP_IP = "127.0.0.1"
TCP_PORT = 12345 
BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def conn():
    print("Sending server request...")
    try:
        s.connect((TCP_IP, TCP_PORT))
        print("Connection successful")
    except Exception as e:
        print(f"Connection unsuccessful. Make sure the server is online. Error: {e}")

def upld(file_name):
    file_path = os.path.join(ROOT_DIRECTORY, file_name)
    print("\nUploading file: {}...".format(file_path))
    
    try:
        with open(file_path, "rb") as content:
            pass
    except FileNotFoundError:
        print("Couldn't open file. Make sure the file name was entered correctly.")
        return
    except Exception as e:
        print(f"Error opening file: {e}")
        return

    try:
        s.send(b"UPLD")
    except Exception as e:
        print(f"Couldn't make server request. Make sure a connection has been established. Error: {e}")
        return

    try:
        s.recv(BUFFER_SIZE)

        file_name_size = struct.pack("h", len(file_name))
        s.send(file_name_size)
        s.send(file_name.encode())

        s.recv(BUFFER_SIZE)
        file_size = os.path.getsize(file_path)
        s.send(struct.pack("i", file_size))
    except Exception as e:
        print(f"Error sending file details: {e}")

    try:
        with open(file_path, "rb") as content:
            print("\nSending...")
            while True:
                l = content.read(BUFFER_SIZE)
                if not l:
                    break
                s.send(l)

        upload_time = struct.unpack("f", s.recv(4))[0]
        upload_size = struct.unpack("i", s.recv(4))[0]
        print("\nSent file: {}\nTime elapsed: {}s\nFile size: {}b".format(file_name, upload_time, upload_size))
    except Exception as e:
        print(f"Error sending file: {e}")
        return

def list_files():
    print("Requesting files...\n")
    try:
        s.send(b"LIST")
    except Exception as e:
        print(f"Couldn't make server request. Make sure a connection has been established. Error: {e}")
        return

    try:
        number_of_files = struct.unpack("i", s.recv(4))[0]

        for i in range(int(number_of_files)):
            file_name_size = struct.unpack("i", s.recv(4))[0]
            file_name = s.recv(file_name_size).decode()
            file_size = struct.unpack("i", s.recv(4))[0]
            print("\t{} - {}b".format(file_name, file_size))

        total_directory_size = struct.unpack("i", s.recv(4))[0]
        print("Total directory size: {}b".format(total_directory_size))
    except Exception as e:
        print(f"Couldn't retrieve listing: {e}")
        return

    try:
        s.send(b"1")
        return
    except Exception as e:
        print(f"Couldn't get final server confirmation: {e}")
        return


def dwld(file_name):
    file_path = os.path.join(ROOT_DIRECTORY, file_name)
    print("Downloading file: {}".format(file_name))
    
    try:
        s.send(b"DWLD")
    except Exception as e:
        print(f"Couldn't make server request. Make sure a connection has been established. Error: {e}")
        return

    try:
        s.recv(BUFFER_SIZE)
        file_name_size = struct.pack("h", len(file_name))
        s.send(file_name_size)
        s.send(file_name.encode())

        file_size = struct.unpack("i", s.recv(4))[0]
        
        if file_size == -1:
            print("File does not exist. Make sure the name was entered correctly")
            return
    except Exception as e:
        print(f"Error checking file: {e}")

    try:
        s.send(b"1")
        output_file = open(file_path, "wb")
        bytes_received = 0
        print("\nDownloading...")
        
        while bytes_received < file_size:
            l = s.recv(BUFFER_SIZE)
            output_file.write(l)
            bytes_received += len(l)
        output_file.close()
        print("Successfully downloaded {}".format(file_name))

        s.send(b"1")

        time_elapsed = struct.unpack("f", s.recv(4))[0]
        print("Time elapsed: {}s\nFile size: {}b".format(time_elapsed, file_size))
    except Exception as e:
        print(f"Error downloading file: {e}")
        return


def delf(file_name):
    print("Deleting file: {}...".format(file_name))
    try:
        s.send(b"DELF")
        s.recv(BUFFER_SIZE)
    except Exception as e:
        print(f"Couldn't connect to the server. Make sure a connection has been established. Error: {e}")
        return

    try:
        file_name_size = struct.pack("h", len(file_name))
        s.send(file_name_size)
        s.send(file_name.encode())
    except Exception as e:
        print(f"Couldn't send file details: {e}")
        return

    try:
        file_exists = struct.unpack("i", s.recv(4))[0]
        if file_exists == -1:
            print("The file does not exist on the server")
            return
    except Exception as e:
        print(f"Couldn't determine file existence: {e}")
        return

    try:
        confirm_delete = input("Are you sure you want to delete {}? (Y/N)\n".format(file_name)).upper()
        
        while confirm_delete not in ["Y", "N", "YES", "NO"]:
            print("Command not recognized, try again")
            confirm_delete = input("Are you sure you want to delete {}? (Y/N)\n".format(file_name)).upper()
    except Exception as e:
        print(f"Couldn't confirm deletion status: {e}")
        return

    try:
        if confirm_delete in ["Y", "YES"]:
            s.send(b"Y")
            delete_status = struct.unpack("i", s.recv(4))[0]
            
            if delete_status == 1:
                print("File successfully deleted")
                return
            else:
                print("File failed to delete")
                return
        else:
            s.send(b"N")
            print("Delete abandoned by the user!")
            return
    except Exception as e:
        print(f"Couldn't delete file: {e}")
        return

def quit_ftp():
    s.send(b"QUIT")
    s.recv(BUFFER_SIZE)
    s.close()
    print("Server connection ended")
    sys.exit()

print("\n\n-------------------- FTP client --------------------\n\nAvailable functions:\nCONN           : Connect to the server\nUPLD file_path : Upload file\nLIST           : List files\nDWLD file_path : Download file\nDELF file_path : Delete file\nQUIT           : Exit")

while True:
    prompt = input("\nEnter a command: ")
    if prompt[:4].upper() == "CONN":
        conn()
    elif prompt[:4].upper() == "UPLD":
        upld(prompt[5:])
    elif prompt[:4].upper() == "LIST":
        list_files()
    elif prompt[:4].upper() == "DWLD":
        dwld(prompt[5:])
    elif prompt[:4].upper() == "DELF":
        delf(prompt[5:])
    elif prompt[:4].upper() == "QUIT":
        quit_ftp()
    else:
        print("Command not recognized! Try again.")