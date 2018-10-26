#things to add to improve the project
    #1. : traces so that could be easily debugged
#------------------------------------------------------------------------------------------------------------------------------------------
#bugs to fix
    #problem 1(FIXED): transactions should be saved in orderddict : if not saved transactions are being retrived and saved in as ordered dictionary 
    #problem 2(FIXED): if previous block entries are changed there should be verification of block chain and it should be found ko before loading the data
    #problem 3: show participants is not working properly, only showing the current owner of the chain
    #problem 4: handle the errors when blockchain.txt is deleted or not present & sombody calls the api
#--------------------------------------------------------------------------------------------------------------------------------------------

#use this package for reduce functionality
import functools 
import os 
import hashlib
import json
from collections import OrderedDict
import pickle

#user created:
import hash_util

# commenting the code to initilize the blockchain with gensis block becuase it
# will now be done in load_json_data

# initializing the blockchain list
#genesis_block = {
#    'key': "",
#    'index': 0,
#    'proof' : '',
#    'transactions': [],
#}
#blockchain = [genesis_block]

blockchain = []
open_transactions = []
owner = 'Tarun'
participants = set(['Tarun'])
MINING_REWARD = 10.0

def unpickle_load_data():
    
    global blockchain
    global open_transactions

    try:
        with open('blockchain.pickle', 'rb') as f:
            file_content = pickle.loads(f.read()) 
            blockchain = file_content['chain']
            open_transactions = file_content['ot']

    #in case the file is present but empty it will throw "IndexError"
    except (IOError, IndexError):
        print("-" * 25)
        print("File not Found") 
        print("-" * 25)
        
        # initializing the blockchain list
        genesis_block = {
            'key': "",
            'index': 0,
            'proof' : '',
            'transactions': [],
        }
        blockchain = [genesis_block]
        open_transactions = []

    finally:
        print("CleanUp")

def pickle_save_data():
    try:
        with open('blockchain.pickle', 'wb') as f:
                f.write(pickle.dumps({'chain' : blockchain, 'ot' : open_transactions}))
    except IOError:
        print("Saving Failed")
    
def json_load_data():
    
    global blockchain
    global open_transactions
    
    try:
        with open('blockchain.txt', 'r') as f:
            
            # read file content 
            file_content = f.readlines()
            
            # the [-1] to account for the \n character at the end of the string retrived from saved file
            blockchain = json.loads(file_content[0][:-1])
            
            # changing the type of transaction dictinaries in blocks from normal dictionaries to OrderedDicts
            updated_blockchain = []
           
            # update the blockchain with data stored in blockchain.txt
            for block in blockchain:
                updated_block = {
                    'key' : block['key'],
                    'index' : block['index'],
                    'proof' : block['proof'],
                    'transactions' : [OrderedDict([('sender',tx['sender']),('recipient',tx['recipient']),('amount',tx['amount'])]) for tx in block['transactions']]
                }
                updated_blockchain.append(updated_block)
            
            blockchain = updated_blockchain
            
            # changing the type of transactions dictionaries from normal dictionaries to OrderedDicts in open_transactions 
            open_transactions = json.loads(file_content[1])
            open_transactions = [OrderedDict([('sender',tx['sender']),('recipient',tx['recipient']),('amount',tx['amount'])]) for tx in open_transactions]
    
    #in case the file is present but empty it will throw "IndexError"
    except (IOError, IndexError):
        print("-"*25)
        print("file not found")
        print("Initializing...")
        print("-"*25)
        
        # initializing the blockchain list
        genesis_block = {
            'key': "",
            'index': 0,
            'proof' : '',
            'transactions': [],
        }
        blockchain = [genesis_block]
        open_transactions = []
            
    finally:
        print("CleanUp")
    
def json_save_data():
    try:
        with open('blockchain.txt','w') as f:
            f.write(json.dumps(blockchain))
            f.write('\n')
            f.write(json.dumps(open_transactions))
    except IOError:
        print("Saving Failed...")

def get_last_blockchain_value():
    """returns last value of current blockchain."""
    if len(blockchain) < 1:
        return None
    return blockchain[-1]

def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']

def verify_open_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])

def add_transaction_value(recipient, amount, sender=owner):
    """
    Args:
        :sender: sender of coins
        :recipient: recipient of coins
        :amount: amount sent
    """
#    transaction = {}
#    transaction['sender'] = sender
#    transaction['recipient'] = recipient
#    transaction['amount'] = amount
    transaction = OrderedDict([('sender',sender),('recipient',recipient),('amount',amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        return True
    return False


def valid_proof(transactions, last_hash, proof_number):
    guess = (str(transactions) + str(last_hash) + str(proof_number)).encode()
    guess_hash = hash_util.hash_string_256(guess) 
    return guess_hash[0:2] == '00'
    
def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_util.compute_hash(last_block)
    proof = 1
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


# process transactions
def mine_block():
    last_block = blockchain[-1]
    computed_hash = hash_util.compute_hash(last_block)
    proof = proof_of_work()
    
#    reward_transaction = {
#        'sender' : 'MINING',
#        'recipient' : owner,
#        'amount' : MINING_REWARD
#    }
    reward_transaction = OrderedDict([('sender','MINING'),('recipient', owner), ('amount',MINING_REWARD)])
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = {
        # metadata
        'key': computed_hash,
        'index': len(blockchain),
        'proof' : proof,
        # data
        'transactions': copied_transactions
    }

    blockchain.append(block)
    for tx in open_transactions:
        participants.add(tx['sender'])
        participants.add(tx['recipient'])
    #pickle_save_data()
    json_save_data()
    return True



def get_transaction_value():
    """returns user input for transaction value to be added to the blockchain."""
    recipient = input("Your transaction recipient: ")
    amount = float(input("Your transaction amount: "))
    return (recipient, amount)


def get_balance(participant):
    sent = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
    open_tx_sent_amt = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    sent.append(open_tx_sent_amt)
    
    recived = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
#    sent_amt = 0
#    for amt in sent:
#        if len(amt) > 0:
#            sent_amt += amt[0]
    sent_amt = functools.reduce(lambda tx_sum, tx_amt : tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, sent, 0) 
    recived_amt = functools.reduce(lambda tx_sum,tx_amt : tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, recived, 0)
#    for amt in recived:
#        if len(amt) > 0:
#            recived_amt += amt[0]
    return recived_amt - sent_amt



def get_user_choice(): 
    return input('Your Choice : ')



def print_block_chain():
    print("-"*50)
    for block in blockchain:
        print("Outputting Block")
        print(block)
    else:
        print("-"*50)


def verify_blockchain():
    for (itr, block) in enumerate(blockchain):
        if itr == 0:
            continue
        if block['key'] != hash_util.compute_hash(blockchain[itr-1]):
            return False
        if not valid_proof(block['transactions'][:-1],block['key'],block['proof']):
            print(block['key'])
            return False
        #pickle_save_data()
        json_save_data()
    return True

#unpickle_load_data()
json_load_data()

# user interface using while loop
while True:
    print("Please Choose :")
    print("1 : Add a new transaction.")
    print("2 : output the blockchain.")
    print("3 : output the blockchain participants.") 
    print("clear : clear the console")
    print("h : Manipulate blockchain.")
    print("m : mine a new block.")
    print("q : Exit Block Chain.")
    
    user_choice =  get_user_choice()
    if user_choice == '1':
        tx = get_transaction_value()
        recipient, amount = tx
        if add_transaction_value(recipient, amount):
            print("Transaction Added")
        else : 
            print("ADD Transaction Failed. Not Enough Balance")
       # print('{} has {:.1f} left in account.'.format(owner,get_balance(owner)))
    elif user_choice == '2':
        print_block_chain()
    elif user_choice == '3':
        print(participants)
    elif user_choice == 'clear':
        os.system('clear')
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {
                # metadata
                'key': '',
                'index': 0,
                # data
                'transactions': [{'sender': owner, 'recipient': 'BadMan2', 'amount': 11}]
            }
    elif user_choice == 'm':
        if mine_block():
            open_transactions = []
    elif user_choice == 'q':
        break
    else:
        print("INVALID INPUT")

    if not verify_blockchain():
        print("INVALID BLOCKCHAIN EXITING")
        break
    
    print('{} has {:.1f} left in account.'.format(owner,get_balance(owner)))
print('Done')
