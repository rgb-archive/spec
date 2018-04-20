from model.RGBOutput import RGBOutput
from model.blockchain.UTXO import UTXO
from model.blockchain.Block import Block
from model.blockchain.Blockchain import Blockchain
from model.blockchain.Transaction import Transaction
from model.contracts.CrowdsaleContract import CrowdsaleContract
from model.proofs.CrowdsaleBuyProof import CrowdsaleBuyProof
from model.proofs.Proof import Proof

"""Example to test the crodwsale issuance procedure

This example shows how to create a crowdsale and how people can buy tokens from
it in a completely non-interactive way.

This is a bit more complex because we need a "blockchain" entity too, in order
to perform queries about the blocks' height. This fake blockchain is actually
pretty scammy: no POW is checked and there can be gaps between blocks.

Fake bitcoin transactions and blocks are also created in this example.

The kind of contract used in this example needs only the issuance_utxo, needed
to store a commitment to the contract on the blockchain.

The contract created acutally issues two different tokens: the "real" token that
can have any price defined by the creator (in SAT) and a "change" token, with a
fixed price of 1 SAT/token, which is needed to return the change when someone
buys some tokens or to send a refund in case all the available tokens have
already been sold.

There's actually a bug (UB) in how the token sale is handled: a clear and
determininstic way to agree on the order of the transactions in the same block
has not (yet) been invented. This could lead to some issues when the tokens are
sold out and we need to agree on who is going to receive the tokens and who is
going to receive the refund. This is still a big TODO. Right now the order of
the transactions in the block is used, because in this fake blocks transactions
are stored in arrays.
"""

# First of all, let's create a scammy blockchain
blockchain = Blockchain([])

# And an UTXO for the issuance
issuance_utxo = UTXO.from_string('asd:1')

# Create the contract with a max supply of 1000 tokens, priced at 10 SAT/each
# The crowdsale will be active between blocks 10 and 15
# All the transactions to buy some tokens must be sent to "crowdsaleaddr"
contract = CrowdsaleContract('Title', issuance_utxo, 1000, 10, 10, 15, 'crowdsaleaddr')
# Then we spend the UTXO to save a commitment to the contract on the blockchain
issuance_utxo.spend()

# Alice tries to buy 999 tokens (by paying 9990 SAT to "crowdsaleaddr")
# The bitcoin transactions created here MUST have only two outputs: one to send
# some SAT to the crowdsale and one which will receive the tokens (and change)
alice_buys_tokens = Transaction('alice_tx', {'alice_rgb_address': 1, 'crowdsaleaddr': 9990})
# Bob tries to buy some tokens too (2)
bob_buys_tokens = Transaction('bob_tx', {'crowdsaleaddr': 20, 'bob_rgb_address': 1})

# Both the transactions are confirmed in block at height 12
Block(12, [alice_buys_tokens, bob_buys_tokens], blockchain)

# Now, since Alice's transaction is the first transaction included in the block
# she will receive all the tokens she tried to buy (999 of the 1000 available)
# and they will be "sent" to the other output in her transaction (alice_tx:0)
# Bob instead will only receive one token, plus 10 "change" tokens as a refund.
# He will receive both those tokens on the output "bob_tx:1"

# Now Bob wants to send the "real" token he got to Carol and his 10 "change"
# tokens to Dave.
carol_utxo = UTXO('fff', 1)
dave_utxo = UTXO('ffb', 0)

# First he creates the two RGBOutput
token_rgb_output = RGBOutput(contract.get_token_id(), 1, carol_utxo)
change_rgb_output = RGBOutput(contract.get_change_token_id(), 10, dave_utxo)

# Then he creates a proof to show that he really bought the tokens, and that now
# they are "bound" to the second output of his initial transaction
bob_buy_proof = CrowdsaleBuyProof(bob_buys_tokens.get_utxo(1), contract, [token_rgb_output, change_rgb_output], blockchain)
# Then he spends the output to save a commitment on the blockchain
bob_buys_tokens.utxos[1].spend()

# Now Carol can send the tokens she got to someone else (in this case, whoever
# will be able to spend the first output of the bitcoin transaction)
spend_output = RGBOutput(contract.get_token_id(), 1, UTXO(None, 0))
carol_spend_proof = Proof(carol_utxo, [bob_buy_proof], [spend_output])
# Then Carol spends her UTXO to (once again) save a commitment on the blockchain
carol_utxo.spend()

assert carol_spend_proof.verify(), "carol_spend_proof is not valid"
