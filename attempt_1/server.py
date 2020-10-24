import socket
import threading
import os
import pathlib
import shutil
from shutil import rmtree
from message import *

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
    rm.recv_buffer = sock.recv(1024)
    rm.process_header()
    rm.recv_buffer += sock.recv(rm.payload_size)
    rm.process_payload()
    if rm.data["instruction_type"] == InstructionType.CREATE_BUCKET.value:
        output = create_bucket(rm.data["bucket_path"])
    elif rm.data["instruction_type"] == InstructionType.REMOVE_BUCKET.value:
    elif rm.data["instruction_type"] == InstructionType.LIST_BUCKETS.value:
    elif rm.data["instruction_type"] == InstructionType.REMOVE_FILE_FROM_BUCKET.value:
    elif rm.data["instruction_type"] == InstructionType.LIST_FILES_FROM_BUCKET.value:
    elif rm.data["instruction_type"] == InstructionType.UPLOAD_FILE.value:
    elif rm.data["instruction_type"] == InstructionType.DOWNLOAD_FILE.value:
    

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
    assert str(bucket_name) == str
    assert path != ""
    path = pathlib.Path(path)
    try:
        path.mkdir(parents = True)
    except FileExistsError as e:
        return f"ERROR: The bucket {path} already exists"
    return f"SUCCESS: Success creating bucket in {path}"

def delete_bucket(path):
    path = Path(path)
    shutil.rmtree(str(path))

def list_buckets(s):
    list = os.system("tree -d")
    s.sendall(bytes(list, "utf-8"))



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
    main()
