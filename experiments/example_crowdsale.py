from model.RGBOutput import RGBOutput
from model.UTXO import UTXO
from model.blockchain.Block import Block
from model.blockchain.Transaction import Transaction
from model.contracts.CrowdsaleContract import CrowdsaleContract
from model.proofs.CrowdsaleBuyProof import CrowdsaleBuyProof
from model.proofs.Proof import Proof

issuance_utxo = UTXO.from_string('asd:1')

contract = CrowdsaleContract('Title', issuance_utxo, 1000, 10, 10, 15, 'crowdsaleaddr')
issuance_utxo.spend()

buy_token = Transaction('buytx', {'abc': 1, 'crowdsaleaddr': 20})
buy_token_block = Block(12, [buy_token])

new_owner_utxo = UTXO('fff', 1)

buy_proof = CrowdsaleBuyProof(buy_token.get_utxo(0), contract, 2, new_owner_utxo)
buy_token.utxos[0].spend()

spend_output = RGBOutput(contract.get_token_id(), 2, UTXO(None, 0))
spend_proof = Proof(new_owner_utxo, [buy_proof], [spend_output])
new_owner_utxo.spend()

print(spend_proof.verify())
