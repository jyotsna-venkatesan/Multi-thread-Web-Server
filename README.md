# Simple HTTP Server

This project implements a basic HTTP server using python that can handle GET requests, serve static files, and manage persistent connections via HTTP keep-alive functionality.

# Student Name and ID

Jyotsna Venkatesan
22108825d

# Compilation and Running

You can use the command line to specify the directory from which files will be served. If no directory is specified, it defaults to `./testfiles`.
To run the server with a specific directory:
Replace `path/to/directory` with the path to the directory containing the files you want to serve.
If you would like to change the default file, modify the line `requested_file = parts[1] if parts[1] != '/' else '/test-image.jpg'`
If you would like to use the default directory and default file, simply run the following line. If not, make the above changes and then run the following line:
python server.py
The server will start on `localhost` at port `8080` which can be accessed by navigating to `http://localhost:8080/`
The server logs each request in the `server.log` file in the current directory
