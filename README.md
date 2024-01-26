# FTP Implementation

This project implements a basic FTP (File Transfer Protocol) server and client using Python's socket programming.

## Features

    - **UPLD (Upload):** Upload a file to the server.
    - **DWLD (Download):** Download a file from the server.
    - **LIST:** List all files on the server.
    - **DELF (Delete):** Delete a file on the server.
    - **QUIT:** Exit the FTP client.

- Each client connection is handled in a separate thread, allowing for simultaneous file transfers between multiple clients and the server.

- The server logs transfer history to a file (`server_log.txt`). 


## Running the project

Open a terminal and run:

    `cd server`

    `python3 server.py`

In separate terminal run:

    `cd client`

    `python3 client.py`

enter `CONN` to establish the connection.

