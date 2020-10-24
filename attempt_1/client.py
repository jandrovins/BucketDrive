#!/usr/bin/env python
import socket
from message import *
import cmd
import sys
import logging
import argparse

def download_file(bucket_name, file_name):
    global HOST
    global PORT

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    data = { "instruction_type": str(InstructionType.DOWNLOAD_FILE.value),
             "bucket_name": bucket_name,
             "file_name": file_name,}
    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    file_size = s.recv(8)
    file_size = struct.unpack(">Q", file_size)[0]
    total_size = file_size

    f = open("new_"+file_name, "wb")
    total_received = 0
    while file_size != 0:
        data = s.recv(4096)      
        file_size -= len(data)
        print("{0:.2f}".format(((total_size-file_size)/float(total_size))*100)+"% Downloaded.")
        f.write(data)



    """
    file_name = input("Filename? ->")

    if file_name != "q":
        s.send(bytes(file_name, "utf-8"))
        data = s.recv(1024)
        #print(data)
        if data[:6] == b"EXISTS":
            file_size = float(data[6:])
            message = input("The file exists, do you want to download it? (Y/N) ->")
            if message == "Y":
                s.send(b"OK")
                file = open("new_"+file_name, "wb")
                data = s.recv(1024)
                total_recieved = len(data)
                file.write(data)
                while total_recieved < file_size:
                    data = s.recv(1024)
                    total_recieved += len(data)
                    file.write(data)
                    print("{0:.2f}".format((total_recieved/float(file_size))*100)+"% Downloaded.")
                print("Download completed!")
                main()
        else:
            print("File does not exist :(")
            main()
    s.close()"""
"""
def upload_file(s):
    file_name = input("Filename? ->")

    if file_name != "q":
        if (os.path.isfile(file_name)):
        with open(file_name, "rb") as f:
            bytes_to_send = f.read()
            s.sendall(bytes_to_send)
    else:
        s.send(b"ERR")
    s.close()
"""
def recv_response(sock):
    rm = ReceivedMessage()
    rm.recv_buffer = sock.recv(8)
    rm.process_header()
    rm.recv_buffer += sock.recv(rm.payload_size)
    rm.process_payload(is_response = True)
    print(rm.data["response"])

def create_bucket(bucket_name):
    global HOST
    global PORT
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    data = { "instruction_type": str(InstructionType.CREATE_BUCKET.value),
             "bucket_name": bucket_name}
    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    recv_response(s)
    
def remove_bucket(bucket_name):
    global HOST
    global PORT
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    data = { "instruction_type": str(InstructionType.REMOVE_BUCKET.value),
             "bucket_name": bucket_name}
    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    recv_response(s)

        
def list_buckets():
    global HOST
    global PORT
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    data = { "instruction_type": str(InstructionType.LIST_BUCKETS.value),}
    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    recv_response(s)

def list_files(bucket_name):
    global HOST
    global PORT
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    data = { "instruction_type": str(InstructionType.LIST_FILES_FROM_BUCKET.value),
             "bucket_name": bucket_name}
    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    recv_response(s)

def remove_bucket(bucket_name):

    global HOST
    global PORT
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    data = { "instruction_type": str(InstructionType.REMOVE_BUCKET.value),
             "bucket_name": bucket_name}
    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    recv_response(s)

def remove_file(bucket_name, file_name):
    global HOST
    global PORT
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    data = { "instruction_type": str(InstructionType.REMOVE_FILE_FROM_BUCKET.value),
             "bucket_name": bucket_name,
             "file_name": file_name}
    message = SentMessage(data=data)
    message_bytes = message.create_message()
    s.sendall(message_bytes)

    recv_response(s)

    
    
class BucketShell(cmd.Cmd):
    intro = "Welcome to Bucket Drive! \n Type ? or help to see commands. \n Type help COMMAND_NAME to see further information about the command. \n Type bye to leave."
    prompt = "-> "
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
        'Uploads a local file to the server: UPLOAD_FILE filePath'
        forward(*parse(arg))
    def do_DOWNLOAD_FILE(self, arg):
        'Downloads a file from the server to your computer: DOWNLOAD_FILE filePath'
        split_args = arg.split()
        download_file(split_args[0], split_args[1])
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
    global HOST
    global PORT
    
    shell = BucketShell()

    try:
        shell.cmdloop()
    except:
        print("Sorry, we were not expecting that.")
        
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
