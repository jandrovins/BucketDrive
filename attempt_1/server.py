import socket
import threading
import os

def retrieve_file(name, s):
    file_name = s.recv(1024)
    if (os.path.isfile(file_name)):
        msg = "EXISTS" + str(os.path.getsize(file_name))
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
        t = threading.Thread(target=retrieve_file, args=("reciebe_thread", c))
        t.start()

    s.close()

if __name__ == "__main__":
    main()
