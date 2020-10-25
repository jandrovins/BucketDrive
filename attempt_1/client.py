#!/usr/bin/env python
import socket
from message import *
import cmd
import sys
import logging
import argparse
import threading
import readline

def create_socket():
    global HOST
    global PORT
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s


def download_file(bucket_name, file_name):
    logging.basicConfig(filename="Client.log",
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s", 
            datefmt='%m/%d/%Y %I:%M:%S %p'
            )

    logging.info(f'Creating a DOWNLOAD_FILE request')

    s = create_socket()

    logging.info(f'Establishing socket connection in {HOST}:{PORT}')

    data = { "instruction_type": str(InstructionType.DOWNLOAD_FILE.value),
             "bucket_name": bucket_name,
             "file_name": file_name,}
    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    logging.info(f'Downloading file with {type(bucket_name)} {bucket_name} AND {type(file_name)} {file_name}')

    header_len = 8
    recv_buffer = b""
    bytes_recd = 0
    while bytes_recd < header_len:
        chunk = s.recv(min(header_len - bytes_recd, header_len))
        if chunk == b"":
            raise RuntimeError("socket connection broken")
        recv_buffer += chunk
        bytes_recd += len(chunk)

    total_size = struct.unpack(">Q", recv_buffer)[0]

    f = open("new_"+file_name, "wb")
    bytes_recd = 0
    while bytes_recd < total_size:
        chunk = s.recv(min(total_size-bytes_recd, 4096))
        f.write(chunk)
        bytes_recd += len(chunk)

    logging.info(f'Received response from server.')

def upload_file(bucket_name, file_name):
    logging.basicConfig(filename="Client.log",
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s", 
            datefmt='%m/%d/%Y %I:%M:%S %p'
            )

    logging.info(f'Creating a UPLOAD_FILE request')

    s = create_socket()

    logging.info(f'Establishing socket connection in {HOST}:{PORT}')

    data = { "instruction_type": str(InstructionType.UPLOAD_FILE.value),
             "bucket_name": bucket_name,
             "file_name": file_name,}
    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    logging.info(f'Uploading file with {type(bucket_name)} {bucket_name} AND {type(file_name)} {file_name}')


    if os.path.isfile(file_name):
        file_size = file_abs_path.stat().st_size
        output = struct.pack(">Q", file_size)
        sock.sendall(output)

        with open(file_abs_path, "rb") as f:
            bytes_to_send = f.read()
            print(type(bytes_to_send))
            sock.sendall(bytes_to_send)
        output = "SUCCESS: The file has been downloaded."
        return output
    else:
        return f"ERROR: File {file_name} does not exist in given bucket"

    logging.info(f'Received response from server.')


def recv_response(sock):
    rm = ReceivedMessage(is_response=True)
    read_message(rm, sock)
    print(rm.data["response"])

def create_bucket(bucket_name):
    logging.basicConfig(filename="Client.log",
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s", 
            datefmt='%m/%d/%Y %I:%M:%S %p'
            )

    logging.info(f'Creating a DOWNLOAD_FILE request')

    s = create_socket()

    logging.info(f'Establishing socket connection in {HOST}:{PORT}')


    data = { "instruction_type": str(InstructionType.CREATE_BUCKET.value),
             "bucket_name": bucket_name}
    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    logging.info(f'Creating bucket with {type(bucket_name)} {bucket_name}')

    recv_response(s)

    logging.info(f'Received response from server')

def remove_bucket(bucket_name):
    logging.basicConfig(filename="Client.log",
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s", 
            datefmt='%m/%d/%Y %I:%M:%S %p'
            )

    logging.info(f'Creating a REMOVE_BUCKET request')

    s = create_socket()

    logging.info(f'Establishing socket connection in {HOST}:{PORT}')

    data = { "instruction_type": str(InstructionType.REMOVE_BUCKET.value),
             "bucket_name": bucket_name}

    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    logging.info(f'removing bucket with {type(bucket_name)} {bucket_name}')

    recv_response(s)

    logging.info(f'Received response from server.')

def list_buckets():
    logging.basicConfig(filename="Client.log",
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s", 
            datefmt='%m/%d/%Y %I:%M:%S %p'
            )

    logging.info(f'Creating a LIST_BUCKETS request')

    s = create_socket()

    logging.info(f'Establishing socket connection in {HOST}:{PORT}')

    data = { "instruction_type": str(InstructionType.LIST_BUCKETS.value),}
    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    logging.info(f'Params: None')

    recv_response(s)

    logging.info(f'Received response from server.')

def list_files(bucket_name):
    logging.basicConfig(filename="Client.log",
        filemode="a",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s", 
        datefmt='%m/%d/%Y %I:%M:%S %p'
        )

    logging.info(f'Creating a LIST_FILES request')

    s = create_socket()

    logging.info(f'Establishing socket connection in {HOST}:{PORT}')

    data = { "instruction_type": str(InstructionType.LIST_FILES_FROM_BUCKET.value),
             "bucket_name": bucket_name}
    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    logging.info(f'Linting files with {type(bucket_name)} {bucket_name}')

    recv_response(s)

    logging.info(f'Received response from server.')

def remove_bucket(bucket_name):
    logging.basicConfig(filename="Client.log",
        filemode="a",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s", 
        datefmt='%m/%d/%Y %I:%M:%S %p'
        )

    logging.info(f'Creating a REMOVE_BUCKET request')

    s = create_socket()

    logging.info(f'Establishing socket connection in {HOST}:{PORT}')

    data = { "instruction_type": str(InstructionType.REMOVE_BUCKET.value),
             "bucket_name": bucket_name}
    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    logging.info(f'Removing bucket with {type(bucket_name)} {bucket_name}')

    recv_response(s)

    logging.info(f'Received response from server.')

def remove_file(bucket_name, file_name):
    logging.basicConfig(filename="Client.log",
        filemode="a",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s", 
        datefmt='%m/%d/%Y %I:%M:%S %p'
        )

    logging.info(f'Creating a REMOVE FILE request')

    s = create_socket()

    logging.info(f'Establishing socket connection in {HOST}:{PORT}')

    data = { "instruction_type": str(InstructionType.REMOVE_FILE_FROM_BUCKET.value),
             "bucket_name": bucket_name,
             "file_name": file_name}
    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    logging.info(f'Removing file with {type(bucket_name)} {bucket_name} AND {type(file_name)} {file_name}')

    recv_response(s)

    logging.info(f'Received response from server.')

class BucketShell(cmd.Cmd):
    intro = "Welcome to Bucket Drive! \n Type ? or help to see commands. \n Type help COMMAND_NAME to see further information about the command. \n Type bye to leave."
    prompt = "BucketDrive-> "
    file = None
    
    # Basic Bucket Drive commands
    def do_CREATE_BUCKET(self, arg):
        'Creates a bucket with a given name: CREATE_BUCKET bucketName'
        create_bucket(str(arg))
    def do_REMOVE_BUCKET(self, arg):
        'Deletes a bucket with a given name: REMOVE_BUCKET bucketName'
        remove_bucket(str(arg))
    def do_LIST_BUCKETS(self, arg):
        'Lists all the buckets in the working directory: LIST_BUCKETS'
        list_buckets()
    def do_REMOVE_FILE_FROM_BUCKET(self, arg):
        'Removes a file from a bucket: REMOVE_FILE_FROM_BUCKET bucketName fileName'
        split_args = arg.split()
        remove_file(split_args[0], split_args[1])
    def do_LIST_FILES_FROM_BUCKET(self, arg):
        'Lists all the files in a given bucket: LIST_FILES_FROM_BUCKET bucketName'
        list_files(str(arg))
    def do_UPLOAD_FILE(self, arg):
        'Uploads a local file to the server: UPLOAD_FILE bucketName fileName'
        split_args = arg.split()
        t = threading.Thread(target=upload_file, args=(split_args[0], split_args[1]))
        t.start()
    def do_DOWNLOAD_FILE(self, arg):
        'Downloads a file from the server to your computer: DOWNLOAD_FILE bucketName fileName'
        split_args = arg.split()
        t = threading.Thread(target=download_file, args=(split_args[0], split_args[1]))
        t.start()
    def do_bye(self, arg):
        'Stop recording, close the turtle window, and exit:  BYE'
        print('Bye bye!')
        self.close()
        return True

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

def main():
    shell = BucketShell()

    try:
        shell.cmdloop()
    except Exception as e:
        print(f"Sorry, we were not expecting that. {e}")
        
if __name__ == "__main__":
    # Manejo de parametros
    parser = argparse.ArgumentParser(description="Create a BucketDrive client")
    parser.add_argument("--port", type=int, metavar="PORT", choices=[i for i in range(1000, 65534)], default = 7777, help="Port on which the client will open sockets. Should be a number between 1000 and 65535. Default is 7777")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host on which the client will run. Default is 127.0.0.1")

    args = parser.parse_args()

    HOST = args.host
    PORT = args.port

    logging.basicConfig(filename="Client.log",
        filemode="a",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s", 
        datefmt='%m/%d/%Y %I:%M:%S %p'
        )

    logging.info(f"STARTED CLIENT USING {HOST}:{PORT}")
    
    main()
