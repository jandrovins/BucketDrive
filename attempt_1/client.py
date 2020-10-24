import socket

def download_file(s):
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
    s.close()
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
def create_bucket(s):
    bucket_path = input("New bucket name? -> ")

    s.sendall(bytes(bucket_path, "utf-8"))  

def delete_bucket(s):
    bucket_path = input("Name of the bucket you want to delete? -> ")

    s.sendall(bytes(bucket_path, "utf-8"))  

def list_buckets(s):
    s.sendall(bytes("list", "utf-8"))  
    list = s.recv(1024)
    s.print(list)
    
def main():
    host = "127.0.0.1"
    port = 7777

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))


    list_buckets(s)
    
if __name__ == "__main__":
    main()
