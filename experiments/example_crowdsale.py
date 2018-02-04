from model.RGBOutput import RGBOutput
from model.UTXO import UTXO
from model.blockchain.Block import Block
from model.blockchain.Blockchain import Blockchain
from model.blockchain.Transaction import Transaction
from model.contracts.CrowdsaleContract import CrowdsaleContract
from model.proofs.CrowdsaleBuyProof import CrowdsaleBuyProof
from model.proofs.Proof import Proof

blockchain = Blockchain([])

issuance_utxo = UTXO.from_string('asd:1')

contract = CrowdsaleContract('Title', issuance_utxo, 1000, 10, 10, 15, 'crowdsaleaddr')
issuance_utxo.spend()

someoneelse_buys_all_tokens = Transaction('someonebuys', {'lll': 1, 'crowdsaleaddr': 9990})

buy_token = Transaction('buytx', {'abc': 1, 'crowdsaleaddr': 20})
buy_token_block = Block(12, [someoneelse_buys_all_tokens, buy_token], blockchain)

new_token_owner_utxo = UTXO('fff', 1)
new_change_owner_utxo = UTXO('ffb', 0)

buy_proof = CrowdsaleBuyProof(buy_token.get_utxo(0), contract, 1, 10, new_token_owner_utxo, new_change_owner_utxo,
                              blockchain)
buy_token.utxos[0].spend()

spend_output = RGBOutput(contract.get_token_id(), 1, UTXO(None, 0))
spend_proof = Proof(new_token_owner_utxo, [buy_proof], [spend_output])
new_token_owner_utxo.spend()

print(spend_proof.verify())
