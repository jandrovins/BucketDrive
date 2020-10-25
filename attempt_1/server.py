#!/usr/bin/env python
import socket
import threading
import os
import pathlib
import shutil
import sys
import logging
import argparse
from message import *

def read(sock):
    logging.info("Reading new connection message")
    rm = ReceivedMessage()
    read_message(rm, sock)
    instruction_type = InstructionType(rm.data['instruction_type'])
    logging.info(f"The data received is: {rm.data}")
    logging.info(f"The instruction type is: {instruction_type.name}")

    if instruction_type == InstructionType.CREATE_BUCKET:
        bucket_name = rm.data["bucket_name"]
        output = create_bucket(bucket_name)
    elif instruction_type == InstructionType.REMOVE_BUCKET:
        bucket_name = rm.data["bucket_name"]
        output = remove_bucket(bucket_name)
    elif instruction_type == InstructionType.LIST_BUCKETS:
        output = list_buckets()
    elif instruction_type == InstructionType.REMOVE_FILE_FROM_BUCKET:
        bucket_name = rm.data["bucket_name"]
        file_name = rm.data["file_name"]
        output = remove_file_from_bucket(str(rm.data["bucket_name"]), str(rm.data["file_name"]))
    elif instruction_type == InstructionType.LIST_FILES_FROM_BUCKET:
        bucket_name = rm.data["bucket_name"]
        output = list_files(bucket_name)
    elif instruction_type == InstructionType.UPLOAD_FILE:
        bucket_name = rm.data["bucket_name"]
        file_name = rm.data["file_name"]
        output = download_file(str(rm.data["bucket_name"]), str(rm.data["file_name"]), sock)
    elif instruction_type == InstructionType.DOWNLOAD_FILE:
        bucket_name = rm.data["bucket_name"]
        file_name = rm.data["file_name"]
        output = download_file(str(rm.data["bucket_name"]), str(rm.data["file_name"]), sock)
    else:
        output = "ERROR: no instruction type was parsed correctly. Check your message"
        logging.error(output.split("."[0]))

    if not "ERROR" in output:
        logging.info("Creating response from server with output: {output}")
    # No matter if succeded of an error occured, send response to client.
    data = {"response":output}
    response = SentMessage(data=data)
    response_bytes = response.create_message()
    sock.sendall(response_bytes)
    

def upload_file(bucket_name, file_name, sock):
    assert issubclass(type(ROOT_PATH), pathlib.Path)
    assert str(ROOT_PATH) != ""
    assert type(bucket_name) == str
    assert type(file_name) == str
    assert bucket_name !=""
    assert file_name !=""

    if not bucket_abs_path.exists():
        return f"ERROR: Bucket '{bucket_name}' does not exist inside root directory '{ROOT_PATH}'"
    file_abs_path = bucket_abs_path / file_name
    print(file_abs_path)
    output = ""

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


    
def create_bucket(bucket_name): # bucket_name can be of the form "some/thing/strange"
    global ROOT_PATH # absolute path to root path
    assert issubclass(type(ROOT_PATH), pathlib.Path)
    assert str(ROOT_PATH) != ""
    assert type(bucket_name) == str
    assert bucket_name != ""
    assert "/" not in bucket_name

    absolute_path = ROOT_PATH / bucket_name

    try:
        absolute_path.mkdir()
    except FileExistsError as e:
        return f"ERROR: The bucket {absolute_path} already exists"
    except e:
        print (e)
    finally:
        if absolute_path.exists(): # was created succesfully
            return f"SUCCESS: Success creating bucket '{bucket_name}'"
        else:
            return f"ERROR: The bucket '{bucket_name}' could not be created in server"

def remove_bucket(bucket_name): # bucket_name can be of the form "some/thing/strange"
    global ROOT_PATH # absolute path to root path
    assert issubclass(type(ROOT_PATH), pathlib.Path)
    assert str(ROOT_PATH) != ""
    assert type(bucket_name) == str
    assert bucket_name != ""
    assert "/" not in bucket_name 

    absolute_path = ROOT_PATH / bucket_name
    try:
        shutil.rmtree(absolute_path.__str__())
    except FileNotFoundError as e:
        return f"ERROR: The bucket {bucket_name} does not exist\b\t{e}"
    finally:
        if not absolute_path.exists(): # was removed succesfully
            return f"SUCCESS: Success removing bucket '{bucket_name}'"
        else:
            return f"ERROR: The bucket '{bucket_name}' could not be removed in server"

def list_buckets():
    global ROOT_PATH
    assert issubclass(type(ROOT_PATH), pathlib.Path)
    assert str(ROOT_PATH) != ""
    output = "" # string to send to client
    
    try:
        for child in ROOT_PATH.iterdir():
            if child.is_dir():
                path_string = child.__str__().rsplit("/")[-1]
                output += path_string + "\n"
    except e:
        print(e)
        output = "ERROR: buckets could not be listed in server!"
    finally:
        if output == "":
            output = "SUCCESS: There are no buckets yet!"
        return output

def remove_file_from_bucket(bucket_name, file_name):
    global ROOT_PATH
    assert issubclass(type(ROOT_PATH), pathlib.Path)
    assert str(ROOT_PATH) != ""
    assert type(bucket_name) == str
    assert type(file_name) == str
    assert bucket_name !=""
    assert file_name !=""

    output = ""
    bucket_abs_path = ROOT_PATH / bucket_name 
    if not bucket_abs_path.exists():
        return f"ERROR: Bucket '{bucket_name}' does not exist inside root directory '{ROOT_PATH}'"
    file_abs_path = bucket_abs_path / file_name 
    try:
        file_abs_path.unlink()

    except FileNotFoundError as e:
        output = f"ERROR: File {file_name} not found on bucket {bucket_name}"
    except:
        output = f"ERROR: File {file_name} could not be removed from {bucket_name}"
    finally:
        if output == "":
            output = f"SUCCESS: File {file_name} has been removed from {bucket_name}"
        return output

def list_files(bucket_name):
    global ROOT_PATH
    assert issubclass(type(ROOT_PATH), pathlib.Path)
    assert str(ROOT_PATH) != ""
    assert type(bucket_name) == str
    assert bucket_name !=""

    bucket_abs_path = ROOT_PATH / bucket_name 
    if not bucket_abs_path.exists():
        return "ERROR: Bucket '{bucket_name}' does not exist inside root directory '{ROOT_PATH}'"

    output = ""
    try:
        for child in bucket_abs_path.iterdir():
            if child.is_file():
                path_string = child.__str__().rsplit("/")[-1]
                output += path_string + "\n"
    except e:
        output = "ERROR: files could not be listed in server!"
    finally:
        if output == "":
            output = "SUCCESS: There are no files inside '{bucket_name}' yet!"
        return output

def download_file(bucket_name, file_name, sock):
    global ROOT_PATH
    assert issubclass(type(ROOT_PATH), pathlib.Path)
    assert str(ROOT_PATH) != ""
    assert type(bucket_name) == str
    assert type(file_name) == str
    assert bucket_name !=""
    assert file_name !=""

    bucket_abs_path = ROOT_PATH / bucket_name
    #print(bucket_abs_path)                                                                                                                                   
    if not bucket_abs_path.exists():
        return f"ERROR: Bucket '{bucket_name}' does not exist inside root directory '{ROOT_PATH}'"
    file_abs_path = bucket_abs_path / file_name
    print(file_abs_path)
    output = ""
    
    if file_abs_path.exists():
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
 
def main():
    global HOST
    global PORT

    logging.debug(f"Creating socket")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.info(f"Binding socket to {HOST}:{PORT}")
    s.bind((HOST, PORT))
    backlog = 5 
    logging.info(f"Socket listening with backlog={backlog}")
    s.listen(backlog)

    print(f"Listening on {HOST}:{PORT}")

    logging.info(f"Accepting connections...")
    while True:
        c, addr = s.accept()
        t = threading.Thread(target=read, args=(c,))
        t.start()

    s.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a BucketDrive server")
    parser.add_argument("--port", type=int, metavar="PORT", choices=[i for i in range(1000, 65534)], default=7777, help="Port on which open the socket. Should be between 1000 and 65535. Default is 7777")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host on which the server will run. Default is 127.0.0.1")
    parser.add_argument("--root", type=str, default="", help="Root directory in which the buckets will be managed. Default is the actual directory")
    
    args = parser.parse_args()
    HOST = args.host
    PORT = args.port
    ROOT_PATH = pathlib.Path(args.root)
    # Configure logging
    logging.basicConfig(filename="Server.log",
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s", 
            datefmt='%m/%d/%Y %I:%M:%S %p'
            )

    if not ROOT_PATH.is_absolute():
        ROOT_PATH = pathlib.Path.cwd() / ROOT_PATH # make absolute path
        ROOT_PATH.mkdir(exist_ok=True)

    logging.info(f"STARTED SERVER ON ROOT PATH {ROOT_PATH}, USING {HOST}:{PORT}")

    main()
