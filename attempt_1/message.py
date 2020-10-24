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
    def __init__(self):
        self.recv_buffer = b"" # bytes received in the server
        self.payload_size = None
        self.data = None

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

    def process_payload(self):
        assert self.payload_size != None
        assert self.data == None
        header_len = self.payload_size # we must have read the header
        if len(self.recv_buffer) >= header_len:
            self.payload =  self.json_decode(self.recv_buffer[:header_len], "utf-8")
            self.recv_buffer[header_len:]
            self.data = {}
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
                        params.append("file_name")
                        params.append("bucket_name")
                    elif value == InstructionType.LIST_FILES_FROM_BUCKET.value:
                        number_of_params_for_instruction = 2
                        params.append("bucket_name")
                    elif value == InstructionType.UPLOAD_FILE.value:
                        number_of_params_for_instruction = 2
                        params.append("name")
                    elif value == InstructionType.DOWNLOAD_FILE.value:
                        number_of_params_for_instruction = 3
                        params.append("file_name")
                        params.append("bucket_name")
            assert number_of_params_received == number_of_params_for_instruction, "There was an error in the json received!"


     
class SubClient:
    def __init__(self, message=None, host=None, port=None):
        self.message = message
        assert host != None
        assert port != None
        self.host = host
        self.port = port
        self.sock = None

    def _send_create_bucket(self):
        assert self.socket != None
        assert self.message != None
        self.sock.sendall(self.message.create_message())


    def send(self):
        self.sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        if self.instruction_type ==  InstructionType.CREATE_BUCKET:
            _send_create_bucket()
        elif self.instruction_type == InstructionType.REMOVE_BUCKET: 
            _send_remove_bucket()
        elif self.instruction_type == InstructionType.LIST_BUCKETS: 
            _list_buckets()
        elif self.instruction_type == InstructionType.REMOVE_FILE_FROM_BUCKET: 
            _remove_file_from_bucket()
        elif self.instruction_type == InstructionType.LIST_FILES_FROM_BUCKET: 
            _list_files_from_bucket()
        elif self.instruction_type == InstructionType.UPLOAD_FILE: 
            _upload_file()
        elif self.instruction_type == InstructionType.DOWNLOAD_FILE: 
            _download_file()
