from enum import Enum
import struct
import json
import io

class InstructionType(Enum):
    CREATE_BUCKET           = 1
    REMOVE_BUCKET           = 2
    LIST_BUCKETS            = 3
    REMOVE_FILE_FROM_BUCKET = 4
    LIST_FILES_FROM_BUCKET  = 5
    UPLOAD_FILE             = 6
    DOWNLOAD_FILE           = 7

class SentMessage:
    def __init__(self, data=None):
        self.data               = data
        self.send_buffer        = None

    def create_header(self):
        assert self.payload_size != None
        self.header_bytes = self.payload_size
        return self.header_bytes

    def create_payload(self): 
        assert self.data != None
        self.payload_bytes = json.dumps(self.data).encode("utf-8")
        self.payload_size = struct.pack(">Q", len(self.payload_bytes))
        return self.payload_bytes
    
    def create_message(self):
        payload_bytes = self.create_payload()
        header_bytes = self.create_header()

        self.send_buffer = header_bytes
        self.send_buffer += payload_bytes
        return self.send_buffer

class ReceivedMessage:
    def __init__(self, is_response=False):
        self.recv_buffer = b"" # bytes received in the server
        self.payload_size = None
        self.data = None
        self.is_response = is_response

    def process_header(self):
        header_len = 8 # since we are using unsigned long long
        if len(self.recv_buffer) >= header_len:
            self.payload_size = struct.unpack(">Q",
                    self.recv_buffer[:header_len])[0] # unpack first 8 bytes. Since it always returns a tuple, select the first value
            self.recv_buffer = self.recv_buffer[header_len:] # since we read the first 8 bits, move onto the rest of the message to read


    def json_decode(self, json_bytes, encoding): # decode json from bytes string
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def process_payload(self, is_response = False):
        assert self.payload_size != None
        assert self.data == None
        header_len = self.payload_size
        if len(self.recv_buffer) >= header_len:
            self.payload =  self.json_decode(self.recv_buffer[:header_len], "utf-8")
            self.recv_buffer[header_len:]
            self.data = {}

            if self.is_response:
                self.data["response"] = self.payload["response"]
                return
            
            params = ["instruction_type"]

            number_of_params_received = 0
            number_of_params_for_instruction = None
            for param in params:
                number_of_params_received +=1
                value = self.payload[param]
                if param == "instruction_type":
                    value = int(value)
                self.data[param] = self.payload[param]
                if param == "instruction_type":
                    self.data[param] = value
                    if value == InstructionType.CREATE_BUCKET.value:
                        number_of_params_for_instruction = 2
                        params.append("bucket_name")
                    elif value == InstructionType.REMOVE_BUCKET.value:
                        number_of_params_for_instruction = 2
                        params.append("bucket_name")
                    elif value == InstructionType.LIST_BUCKETS.value:
                        number_of_params_for_instruction = 1
                        pass
                    elif value == InstructionType.REMOVE_FILE_FROM_BUCKET.value:
                        number_of_params_for_instruction = 3
                        params.append("bucket_name")
                        params.append("file_name")
                    elif value == InstructionType.LIST_FILES_FROM_BUCKET.value:
                        number_of_params_for_instruction = 2
                        params.append("bucket_name")
                    elif value == InstructionType.UPLOAD_FILE.value:
                        number_of_params_for_instruction = 3
                        params.append("bucket_name")
                        params.append("file_name")
                    elif value == InstructionType.DOWNLOAD_FILE.value:
                        number_of_params_for_instruction = 3
                        params.append("bucket_name")
                        params.append("file_name")
            assert number_of_params_received == number_of_params_for_instruction, "There was an error in the json received!"

def read_message(rm, sock):
    header_len = 8

    rm.recv_buffer = b""
    bytes_recd = 0
    while bytes_recd < header_len:
        chunk = sock.recv(min(header_len - bytes_recd, 8))
        if chunk == b"":
            raise RuntimeError("socket connection broken")
        rm.recv_buffer += chunk
        bytes_recd += len(chunk)

    rm.process_header()

    rm.recv_buffer = b""
    bytes_recd = 0
    while bytes_recd < rm.payload_size:
        chunk = sock.recv(min(rm.payload_size - bytes_recd, 8))
        if chunk == b"":
            raise RuntimeError("socket connection broken")
        rm.recv_buffer += chunk
        bytes_recd += len(chunk)
    rm.process_payload()
