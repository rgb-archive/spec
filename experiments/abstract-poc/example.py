from model.RGBOutput import RGBOutput
from model.blockchain.UTXO import UTXO
from model.contracts.Contract import Contract
from model.proofs.IssuanceProof import IssuanceProof
from model.proofs.Proof import Proof

"""Basic example to test a chain of proofs

This example shows how to issue a token and transfer it using a chain of proofs.

The kind of contract used in this example needs two UTXOs: the first one, the
issuance_utxo, is needed to store a commitment to the contract, while the second
one receives all the issued token and can spend them by showing a proof.

The first proof is generally a contract-specific kind of proof: it is needed
because every contract has different conditions. All the subsequent proofs will
be generic proofs.

After the creation of every proof the UTXO that holds the tokens is spent with
a commitment to the newly-created proof.
"""

# Create two new UTXO, one for the issuance and one to hold all the tokens
issuance_utxo = UTXO.from_string('asd:1')
owner_utxo = UTXO.from_string('bcd:0')

# Create the contract with a issuance of 1000 tokens
contract = Contract('Title', issuance_utxo, owner_utxo, 1000)
# Spend the issuance_utxo to save a commitment to the contract on the blockchain
issuance_utxo.spend()

# Create the first proof of the chain that "connects" to the contract
issuance_proof = IssuanceProof(issuance_utxo, contract)
# Create a new RGBOutput to spend all the tokens and send them to the first
# output of the bitcoin transaction
spend_output = RGBOutput(contract.get_token_id(), 1000, UTXO(None, 0))
# Create the generic proof to transfer the tokens
spend_proof = Proof(owner_utxo, [issuance_proof], [spend_output])
# Spend the UTXO to save a commitment to the proof on the blockchain
owner_utxo.spend()

print(contract, '\n')
print(issuance_proof, '\n')
print(spend_proof, '\n')

assert spend_proof.verify(), "Invalid spend_proof"
