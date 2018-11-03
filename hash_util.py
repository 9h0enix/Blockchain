import hashlib
import json


def hash_string_256(string):
     return hashlib.sha256(string).hexdigest()

def compute_hash(block):
#    hash_key = str(block['index']) + block['key']
#    for tx in block['transactions']:
#        hash_key += tx['sender'] + tx['recipient'] + str(tx['amount']) + '-'
#    return hash_key
     # need a copy of dictionary for the hash block
     hashable_block = block.__dict__.copy()
     return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())


