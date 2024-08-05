

import time
import datetime
import os
import json
import boto3
import base64

accesskey="QUtJQVdVS09MUUhVUTJBVTM2TVk="
secretkey="SlQwb3ZXazJETzRoc2pCc2VsZVBVd2llRGJLSk0rSk5yUHExUHltMQ=="
s3 = boto3.client(
    's3',
    aws_access_key_id= base64.b64decode(accesskey.encode('utf-8')).decode('utf-8'),
    aws_secret_access_key=base64.b64decode(secretkey.encode('utf-8')).decode('utf-8')
)
S3_BUCKET_NAME = 'arcanabucket123'
from block import Block


INITIAL_BITS = 0x1d777777
MAX_32BIT = 0xffffffff
# AUTH = [Wallet("Authority 1",1), Wallet("Authority 2",1), Wallet("Authority 3",1)]


class BlockEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):  # Check if the object is a datetime instance
            return obj.isoformat()  # Serialize datetime object using ISO format
        elif isinstance(obj, Block):
            return obj.to_json()  # Serialize Block object using its dictionary representation
        return json.JSONEncoder.default(self, obj)

class BlockDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.dict_to_block, *args, **kwargs)

    def dict_to_block(self, dct):
        if all(k in dct for k in ["index", "bits", "nonce", "prev_hash","transactions", "timestamp", "author", "signatures", "elapsed_time", "hash"]):
            iso_timestamp = dct["timestamp"].replace('/', '-').replace(' ', 'T')
            timestamp = datetime.datetime.fromisoformat(iso_timestamp)
            b=Block(dct["bits"], dct["index"], dct["transactions"], timestamp, dct["prev_hash"],dct["author"])
            b.signatures = dct["signatures"]
            b.hash = dct["hash"]
            b.elapsed_time = dct["elapsed_time"]
            b.nonce = dct["nonce"]
            return b
        return dct

        
class Blockchain:
    def __init__(self):
        self.blockchain = self.load_blocks()
    
    def get_chain_length(self):
        return len(self.blockchain)
        
    def getblockinfo(self):
       return print(json.dumps(self.blockchain, indent=2,sort_keys=True, ensure_ascii = False, cls = BlockEncoder))

    def add_block(self, block):
        self.blockchain.append(block)
        self.save_block(self.blockchain)


    def mining(self, block):
        if len(self.blockchain) == 0:
            block.prev_hash = ""
        else:
            block.prev_hash = self.blockchain[-1].hash
        block.index= self.get_chain_length()
        if self.is_block_valid(block):
            start_time = int(time.time() * 1000)
            for n in range(MAX_32BIT + 1):
                block.nonce = n
                if block.check_valid_hash():
                    new_bits = self.get_retarget_bits()
                    if new_bits < 0 :
                        if len(self.blockchain) < 2:
                            block.bits = INITIAL_BITS
                        else:
                            block.bits = self.blockchain[-1].bits
                    else:
                        block.bits = new_bits
                    end_time = int(time.time()*1000)
                    block.elapsed_time = str((end_time - start_time) / (1000.0)) + "秒"
                    self.blockchain.append(block)
                    self.save_block(self.blockchain)
                    return
        else:
            return False
    def get_retarget_bits(self):
      if len(self.blockchain) == 0 or len(self.blockchain) % 5 != 0:
        return -1
      expected_time = 140 * 5

      counter = int(len(self.blockchain)/5)

      first_block = self.blockchain[5*(counter-1)]

      last_block = self.blockchain[-1]

      first_time = first_block.timestamp.timestamp()
      last_time = last_block.timestamp.timestamp()
      total_time = last_time - first_time
      
      target = last_block.calc_target()
      
      delta = total_time / expected_time
      if delta < 0.25:
        delta = 0.25
      if delta > 4:
        delta = 4
      new_target = int(target * delta)

      exponent_bytes = (last_block.bits >> 24) -3
      exponent_bits = exponent_bytes * 8
      temp_bits = new_target >> exponent_bits
      if temp_bits != temp_bits & 0xffffff: # if new target is too big
        exponent_bytes += 1
        exponent_bits += 8
      elif temp_bits == temp_bits & 0xffff:# if new target si too small
        exponent_bytes -= 1
        exponent_bits -= 8
      return ((exponent_bytes + 3) << 24) | (new_target >> exponent_bits) 

    def is_block_valid(self,current_block):
        i = len(self.blockchain)-1
        previous_block = self.blockchain[i]
        if (current_block.index - previous_block.index != 1) :
            print("block index invalid")
            return  False
        if current_block.prev_hash != previous_block.hash:
            print("current block previous hash invalid")
            return False
        return True
    
     
    def save_block(self,block):
        # Save the blocks to a file
        with open("blocks.dat", "wb") as f:
            data=json.dumps(block, cls = BlockEncoder)
            f.write(data.encode('utf-8'))
            print("Block is added to the blockchain")
        f.close()

    def load_blocks(self):
        # Load the blocks from a file
        response= s3.get_object(Bucket=S3_BUCKET_NAME, Key="blocks.dat")
        current_chain_data = response['Body'].read().decode()
        current_chain = json.loads(current_chain_data, cls=BlockDecoder)
        try:
            if os.path.getsize("blocks.dat"):
                with open("blocks.dat", "rb") as f:
                    blocks_data = json.load(f, cls=BlockDecoder)
                    local_chain = [b for b in blocks_data if isinstance(b, Block)]
                if (len(current_chain) > len(local_chain)) | (len(current_chain)==len(local_chain)):
                    print("current")
                    return current_chain
                else:
                    print("local")
                    return local_chain
                
        except FileNotFoundError:
            print("current")
            return current_chain
