import socket
import threading
import os
from pathlib import Path
import shutil
from shutil import rmtree

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

def create_bucket(s):
    path = Path(s.recv(1024).decode("utf-8") )
    path.mkdir(parents = True)

def delete_bucket(s):
    path = Path(s.recv(1024).decode("utf-8") )
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
        t = threading.Thread(target=list_buckets, args=(c,))
        t.start()

    s.close()

if __name__ == "__main__":
    main()
