from model.Contract import Contract
from model.RGBOutput import RGBOutput
from model.UTXO import UTXO
from model.proofs.IssuanceProof import IssuanceProof
from model.proofs.Proof import Proof

issuance_utxo = UTXO.from_string('asd:1')
owner_utxo = UTXO.from_string('bcd:0')

contract = Contract('Title', issuance_utxo, owner_utxo, 1000)
issuance_proof = IssuanceProof(issuance_utxo, contract)

spend_output = RGBOutput(contract.get_token_id(), 1000, UTXO(None, 0))
spend_proof = Proof(owner_utxo, [issuance_proof], [spend_output])

print(contract, '\n')
print(issuance_proof, '\n')
print(spend_proof, '\n')

spend_proof.verify()
