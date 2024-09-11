import socket
from datetime import datetime
import threading
import os
import email.utils  

BASE_DIR = "./testfiles"

# function to parse HTTP request headers from the request lines
def parse_headers(request_lines):
    headers = {}
    for line in request_lines[1:]:
        if ": " in line:
            key, value = line.split(": ", 1)
            headers[key.strip()] = value.strip()
    return headers

# function to generate HTTP response headers based on file existence, modification time, and connection type
def generate_response_headers(file_path, file_exists, if_modified_since=None, keep_alive=False):
    if file_exists:
        file_size = os.path.getsize(file_path)
        file_last_modified = os.path.getmtime(file_path)
        file_last_modified_dt = datetime.utcfromtimestamp(file_last_modified) 

        if if_modified_since:
            if_modified_since = if_modified_since.replace(tzinfo=None)

        if if_modified_since and if_modified_since >= file_last_modified_dt:
            response = "HTTP/1.1 304 Not Modified\n"
        else:
            content_type = "image/jpeg" if file_path.endswith(".jpg") else "text/html"
            response = f"HTTP/1.1 200 OK\nContent-Type: {content_type}\nContent-Length: {file_size}\nLast-Modified: {email.utils.formatdate(file_last_modified, usegmt=True)}\n"
    else:
        response = "HTTP/1.1 404 Not Found\n"

    response += "Connection: keep-alive\n\n" if keep_alive else "Connection: close\n\n"
    return response

# function to log each HTTP request with details about the client, request, and response type
def log_request(client_ip, timestamp, request_line, response_type):
    log_entry = f"{client_ip} - [{timestamp}] \"{request_line}\" {response_type}\n"
    with open("server.log", "a") as log:
        log.write(log_entry)

# function to handle the incoming client connection, processes HTTP requests, and sends responses
def handle_client_connection(client_socket, client_address):
    try:
        keep_alive = True
        while keep_alive:
            request = client_socket.recv(1024).decode('utf-8')
            request_lines = request.splitlines()
            if request_lines:
                request_line = request_lines[0]
                headers = parse_headers(request_lines)
                if_modified_since = email.utils.parsedate_to_datetime(headers.get('If-Modified-Since')) if 'If-Modified-Since' in headers else None
                keep_alive = headers.get('Connection', '').lower() == 'keep-alive'

                print(f"Received request from {client_address[0]}:")
                print(request)
                timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S")
                log_request(client_address[0], timestamp, request_line, "200")  

                parts = request_line.split()
                if len(parts) > 1 and parts[0] in ['GET', 'HEAD']:
                    requested_file = parts[1] if parts[1] != '/' else '/test-image.jpg'
                    file_path = os.path.join(BASE_DIR, requested_file.lstrip('/'))
                    file_exists = os.path.isfile(file_path)
                    response = generate_response_headers(file_path, file_exists, if_modified_since, keep_alive)

                    if parts[0] == 'GET' and file_exists and '304 Not Modified' not in response:
                        with open(file_path, 'rb') as file:
                            response = response.encode('utf-8') + file.read()
                else:
                    response = "HTTP/1.1 400 Bad Request\n\n"
                    log_request(client_address[0], timestamp, request_line, "400")
            else:
                response = "HTTP/1.1 400 Bad Request\n\n"
                log_request(client_address[0], timestamp, "<No Request Line>", "400")

            client_socket.sendall(response.encode('utf-8') if isinstance(response, str) else response)
            if not keep_alive:
                break
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        if not keep_alive:
            client_socket.close()

# function to start the HTTP server on a specified host and port, using the given directory for serving files
def start_server(host='localhost', port=8080, base_dir=None):
    global BASE_DIR
    if base_dir is not None:
        BASE_DIR = base_dir
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"HTTP Server is running on {host}:{port} using base directory '{BASE_DIR}'...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established from {client_address}")
        thread = threading.Thread(target=handle_client_connection, args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        start_server(base_dir=sys.argv[1])
    else:
        start_server()