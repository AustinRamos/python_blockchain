import hashlib
import json

from textwrap import dedent
from time import time
from uuid import uuid4
from urllib.parse import urlparse
from flask import Flask, jsonify, request

class Blockchain(object): 
	#initialize blockchain, set chain to empty list, transactions to empty list
	def __init__(self):
		self.current_transactions=[]
		self.chain = []
		self.nodes = set()
		
        # Create the genesis block
		self.new_block(previous_hash='1', proof=100)

	def valid_chain(self,chain):
		#determine if valid given list of chain, return true if valis false if not, 
		last_block = chain[0]
		current_index = 1
		#simple looping thru linkedlist keeping track of prev(last block)
		while current_index < len(chain):
			block = chain[current_index]
			print(f'{last_block}')
			print(f'{block}')
			print("\n-----------\n")
			#check that hash of block(with last block) is correct
			if(block['previous_hash']!=self.hash(last_block)):
				return False
			
			#check PoW is correct
			
			if not self.valid_proof(last_block['proof'], block['proof']):
				return False;
			last_block = block
			current_index+=1
			
			
			
		return True #if here then entire chain is valid
	

	#Consensus algo, replaces chain with longest in network
	def resolve_conflicts(self):
		neighbors = self.nodes #list of all other nodes in network
		new_chain = None
		
		#look for chains longer than ours
		max_length = len(self.chain)
		
		for node in neighbors:
			#gets address of other nodes
			response = requests.get(f'http://{node}/chain')
		
			if response.status_code==200: #if succesfull connection
				length = response.json()['length']
				chain = response.json()['chain']
				
				#check length
				if length > max_length and self.valid_chain(chain):
					max_length = length
					new_chain = chain
					
				if new_chain: #if not null
					self.chain = new_chain #replace our chain with new chain
					return True;
			return False #return false if chain not replaced
				
				
		
	def register_node(self,address):
		""""
		adds new node to list of nodes
		param -> address of node i.e ip address
		"""
		parsed_url = urlparse(address)
		self.nodes.add(parsed_url.netloc)
		
	
#prev_hash syntax means its optional
	def new_block(self,proof,previous_hash=None): #creates new block , adds to chain
		#this is called in conscrutcof, also generally to create new block
		""""
		param proof <int> : proof given by proof of work algo
		prv_hash (optionsl)
		return <dict> the new block as a list of transactions
		"""
		
		block = {
		
		'index': len(self.chain) + 1, #len of current list + 1 for index, incremental simple
		'timestamp': time(),
		'proof': proof,
		'transactions': self.current_transactions,
		'previous_hash' : previous_hash or self.hash(self.chain[-1])
		}
		#reset currlist of transactions
		self.current_transactions = []
		
		self.chain.append(block)
		return block
		
		
		
		#adds new transaction to the list (of transactions)
	def new_transaction(self,sender,recipient,amount):
		#str,str,int -> returns int index of block that wil hod the transaction
		
		self.current_transactions.append(
		{'sender':sender,
		 'recipient': recipient,
		 'amount': amount,
		})
		
		return self.last_block['index'] + 1
	
		
	@staticmethod
	def hash(block): # hashes a block
		#creates sha-256 hash of a block. 
		#param <dict> block
		#return <str>
		
		block_string = json.dumps(block,sort_keys = True).encode()
		return hashlib.sha256(block_string).hexdigest()
		
		
	@property
	def last_block(self): #returns last block in the chain
		return self.chain[-1]
		
		
	def proof_of_work(self,last_proof):
	
		proof = 0
		while self.valid_proof(last_proof, proof) is False:
		 proof += 1

		return proof
		
        
	@staticmethod
	def valid_proof(last_proof, proof):
      
         guess = f'{last_proof}{proof}'.encode()
         guess_hash = hashlib.sha256(guess).hexdigest()
         return guess_hash[:4] == "0000"
	




#SERVER SIDE STUFF

#instantiate our blockchain node
app = Flask(__name__)

#generate globally unique address for node
node_identifier = str(uuid4()).replace('-','')

#instantiate
blockchain = Blockchain()

@app.route('/mine',methods=['GET'])
def mine():
	#proof of work!
	last_block = blockchain.last_block
	last_proof = last_block['proof']
	proof = blockchain.proof_of_work(last_proof);
	
	#reward for proof: sender is 0 to signifiy coinbase)1st transaction of new block)
	blockchain.new_transaction(
		sender="0",
		recipient=node_identifier,
		amount=1,
	)
	
	#add the block to the chain
	previous_hash = blockchain.hash(last_block)
	block = blockchain.new_block(proof,previous_hash)
	response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
	return jsonify(response),200


@app.route('/transactions/new',methods=['POST'])
def new_transaction():
	values = request.get_json()
	
	#check all required fields have been passed to a post transaction
	required = ['sender','recipient','amount']
	if not all(k in values for k in required):
		return 'Missing Values',400
	
	#create new transaction
	index = blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])

	response = {'message': f'Transaction will be added to Block {index}'}
	return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)

			
