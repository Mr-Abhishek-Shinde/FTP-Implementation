import socket
import sys
import time
import os
import struct
import threading
import json
import logging

ROOT_DIRECTORY = "SERVER_DATA"
TCP_IP = "127.0.0.1"
TCP_PORT = 12345
BUFFER_SIZE = 1024

console_lock = threading.Lock()

logging.basicConfig(filename='server_log.txt', level=logging.INFO, format='%(message)s')

def log(message):
    logging.info(message)

def handle_client(conn, addr):
    client_address = f"Client Address: {addr}"
    log(json.dumps({'client_address': client_address,  'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}))
    
    while True:
        try:
            data = conn.recv(BUFFER_SIZE).decode()
            received_instruction = f"Received instruction from {addr}: {data}"
            log(json.dumps({'received_instruction': received_instruction, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}))

            if data == "UPLD":
                upld(conn)
            elif data == "LIST":
                list_files(conn)
            elif data == "DWLD":
                dwld(conn)
            elif data == "DELF":
                delf(conn)
            elif data == "QUIT":
                quit_ftp(conn)
                break
        except Exception as e:
            error_message = f"Error handling client {addr}: {e}"
            log(json.dumps({'error_message': error_message, 'timestamp': time.time()}))
            break

def upld(conn):
    conn.send(b"1")
    file_name_size = struct.unpack("h", conn.recv(2))[0]
    file_name = conn.recv(file_name_size).decode()
    full_file_path = os.path.join(ROOT_DIRECTORY, file_name)

    conn.send(b"1")
    file_size = struct.unpack("i", conn.recv(4))[0]

    start_time = time.time()
    output_file = open(full_file_path, "wb")
    bytes_received = 0

    print("\nReceiving...")
    while bytes_received < file_size:
        l = conn.recv(BUFFER_SIZE)
        output_file.write(l)
        bytes_received += len(l)
    output_file.close()
    print("\nReceived file: {}".format(file_name))

    conn.send(struct.pack("f", time.time() - start_time))
    conn.send(struct.pack("i", file_size))
    return


def list_files(conn):
    print("Listing files...")
    listing = os.listdir(ROOT_DIRECTORY)

    conn.send(struct.pack("i", len(listing)))
    total_directory_size = 0

    for i in listing:
        conn.send(struct.pack("i", len(i)))
        conn.send(i.encode())
        conn.send(struct.pack("i", os.path.getsize(os.path.join(ROOT_DIRECTORY, i))))
        total_directory_size += os.path.getsize(os.path.join(ROOT_DIRECTORY, i))

    conn.send(struct.pack("i", total_directory_size))
    print("Successfully sent file listing")
    return

def dwld(conn):
    conn.send(b"1")
    file_name_length = struct.unpack("h", conn.recv(2))[0]
    print(file_name_length)
    file_name = conn.recv(file_name_length).decode()
    print(file_name)
    full_file_path = os.path.join(ROOT_DIRECTORY, file_name)
    
    if os.path.isfile(full_file_path):
        conn.send(struct.pack("i", os.path.getsize(full_file_path)))
    else:
        print("File name not valid")
        conn.send(struct.pack("i", -1))
        return

    conn.recv(BUFFER_SIZE)

    start_time = time.time()
    print("Sending file...")
    content = open(full_file_path, "rb")

    l = content.read(BUFFER_SIZE)
    while l:
        conn.send(l)
        l = content.read(BUFFER_SIZE)
    
    content.close()
    conn.recv(BUFFER_SIZE)

    conn.send(struct.pack("f", time.time() - start_time))
    return

def delf(conn):
    conn.send(b"1")
    file_name_length = struct.unpack("h", conn.recv(2))[0]
    file_name = conn.recv(file_name_length).decode()
    full_file_path = os.path.join(ROOT_DIRECTORY, file_name)

    if os.path.isfile(full_file_path):
        conn.send(struct.pack("i", 1))
    else:
        conn.send(struct.pack("i", -1))
        return

    confirm_delete = conn.recv(BUFFER_SIZE).decode()
    if confirm_delete == "Y":
        try:
            os.remove(full_file_path)
            conn.send(struct.pack("i", 1))
        except Exception as e:
            print("Failed to delete {}: {}".format(full_file_path, e))
            conn.send(struct.pack("i", -1))
    else:
        print("Delete abandoned by the client!")
        return
    
def quit_ftp(conn):
    with console_lock:
        print("\nHandling QUIT...")
    conn.send(b"1")
    conn.close()
    with console_lock:
        print("Connection closed.")

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(5)
    with console_lock:
        print("Server listening on {}:{}".format(TCP_IP, TCP_PORT))

    try:
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
    except KeyboardInterrupt:
        with console_lock:
            print("Server shutting down.")
    finally:
        s.close()

if __name__ == "__main__":
    main()