from time import time

class Block:
    
    def __init__(
    self, 
    index, 
    previous_hash, 
    transactions, 
    proof_of_work,
    time_stamp=None
    ):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof_of_work = proof_of_work
        self.time_stamp = time() if time_stamp is None else time_stamp

        
