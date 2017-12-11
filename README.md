# python_blockchain

This is a very simple blockchain I implemented in python to help understand decentralized consensus and 
proof of work in practice, as I have had a difficult time conceptualizing the theory that I have read so much about.

The Blockchain class itself, in memory, keeps track of the nodes registered on the blockchain(each comprised only of a 
unique IP address). This is a set as nodes must be unique.
The Blockchain also keeps a list of the current transactions, and a list of the chain itself(a list of block objects).
When the blockchain is initialized it will also manually create the genesis block, with an index of 1, a Nonce value of
100, and no transactions.
the blocks and transactions are both stores as JSON objects, example transactions and blocks are written below:
block = {
		
		'index': 1 
		'timestamp': time(),
		'proof': proof,
		'transactions': self.current_transactions,
		'previous_hash' : hash_of_prev_block
		}
		
		A block has a unique index(i.e height), a unique timestamp(UNIX time()), a proof(equivalent of a "Nonce", i.e the number appended 
		to the hash to find the target hash that starts with "0000".
		It also contains a list of current transactions(which is reset each time a new block is mined and those transactions are put in the block,
		as well as a hash of the previous block for validation purposes.
		
		
		Transaction = {'sender':sender,
		 'recipient': recipient,
		 'amount': amount,
		}
		
		sender and recipient values are public key addresses. amount is the amount of  'currency' to be sent by the blockchain
		sender is 0 for coinbase(first transaction by miner on a new block for reward of 1 coin).
		

I use flask to set up a very simple server with a few endpoints.

http://localhost:5000/mine
This endpoint will mine a block, and award 1 coin to the node who mined. it will find a 'proof' val for which the hash starts "0000".
It will then make a new block with the blockchains list of current_transactions, that nonce value, an index of the last block+1,
the previous block hash, and a timestamp(then current_transactions is reset for the next block. 

http://localhost:5000/transactions/new'
this is an endpoint which takes POST requests in the form of a transaction in its JSON object(shown above). 
if the transaction is valid(i.e it has a recipient, sender, amount, and no additional information, it will be added to the current
list of transactions.

http://localhost:5000/chain'
This will return the entire chain, each block with all the transaction of each block, all listed in JSON format.


http://localhost:5000/nodes/register
this is an endpoint which takes POST requests in the form of lists of nodes(unique ip addresses), and adds them to the network
(i.e the set of nodes in the blockchain class).



http://localhost:5000/nodes/resolve
if there are nodes with different blockchains, we will find the longest valid blockchain and make it replace it for all nodes.


To validate any given chain, we iterate through the list of blocks, keeping track of the current block and of the last block.
for each iteration, we check that the "previous_hash" field of the current block is equal to the value we get when we
actually rehash the pointer to the previous block. for each block we also check that the Proof of Work for each block 
is correct(that the hash starts with "0000").

