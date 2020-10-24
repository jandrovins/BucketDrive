import socket
import threading
import os
import pathlib
import shutil
import sys
from message import *

ROOT_PATH=None

def download_file(s):
    file_name = s.recv(1024)
    if (os.path.isfile(file_name)):
        msg = "EXISTS" + str(os.path.getsize(file_name))
        print(str(os.path.getsize(file_name)))
        s.send(bytes(msg, "utf-8"))
        user_response = s.recv(1024)
        if (user_response[:2] == b"OK"):
            with open(file_name, "rb") as f:
                bytes_to_send = f.read(1024)
                s.send(bytes_to_send)
                while bytes_to_send:
                    bytes_to_send = f.read(1024)
                    s.send(bytes_to_send)
    else:
        s.send(b"ERR")
    s.close()

def read(sock):
    from time import sleep
    rm = ReceivedMessage()
    rm.recv_buffer = sock.recv(8)
    rm.process_header()
    rm.recv_buffer += sock.recv(rm.payload_size)
    rm.process_payload()
    if rm.data["instruction_type"] == InstructionType.CREATE_BUCKET.value:
        output = create_bucket(rm.data["bucket_name"])
    elif rm.data["instruction_type"] == InstructionType.REMOVE_BUCKET.value:
        output = remove_bucket(rm.data["bucket_name"])
    elif rm.data["instruction_type"] == InstructionType.LIST_BUCKETS.value:
        output = list_buckets()
    elif rm.data["instruction_type"] == InstructionType.REMOVE_FILE_FROM_BUCKET.value:
        output = remove_file_from_bucket(str(rm.data["bucket_name"]), str(rm.data["file_name"]))
    elif rm.data["instruction_type"] == InstructionType.LIST_FILES_FROM_BUCKET.value:
        output = list_files(rm.data["bucket_name"])
    elif rm.data["instruction_type"] == InstructionType.UPLOAD_FILE.value:
        pass
    elif rm.data["instruction_type"] == InstructionType.DOWNLOAD_FILE.value:
        pass
    else:
        output = "ERROR: no instruction type was parsed correctly. Check your message"

    # No matter if succeded of an error occured, send response to client.
    data = {"response":output}
    response = SentMessage(data=data)
    response_bytes = response.create_message()
    sock.sendall(response_bytes)
    

def upload_file(s):
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
    s.close()

def create_bucket(bucket_name): # bucket_name can be of the form "some/thing/strange"
    global ROOT_PATH # absolute path to root path
    assert issubclass(type(ROOT_PATH), pathlib.Path)
    assert str(ROOT_PATH) != ""
    assert type(bucket_name) == str
    assert bucket_name != ""
    assert "/" not in bucket_name

    absolute_path = ROOT_PATH / bucket_name
    print(f"--------AP: {absolute_path}, ROOT_PATH: {ROOT_PATH}, bucket_name: {bucket_name}")

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
            output = "There are no buckets yet!"
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
        return "ERROR: Bucket '{bucket_name}' does not exist inside root directory '{ROOT_PATH}'"
    file_abs_path = bucket_abs_path / bucket_name 
    try:
        file_abs_path.unlink()

    except FileNotFoundError as e:
        output = "ERROR: File {file_name} not found on bucket {bucket_name}"
    except:
        output = "ERROR: File {file_name} could not be removed from {bucket_name}"
    finally:
        if output == ""
            output = "SUCCESS: File {file_name} has been removed from {bucket_name}"
        return output

def main():
    host = "127.0.0.1"
    port = 7777

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)

    print("Server started!")

    while True:
        c, addr = s.accept()
        print(c)
        print(f"Client connected ip:<{addr}>")
        t = threading.Thread(target=read, args=(c,))
        t.start()

    s.close()


if __name__ == "__main__":
    ROOT_PATH = pathlib.Path(sys.argv[1])
    if not ROOT_PATH.is_absolute():
        ROOT_PATH = pathlib.Path.cwd() / ROOT_PATH # make absolute path
    main()
