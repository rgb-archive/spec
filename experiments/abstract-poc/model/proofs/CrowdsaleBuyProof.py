import math
from functools import reduce
from typing import List

from model.RGBOutput import RGBOutput
from model.blockchain.Blockchain import Blockchain
from model.blockchain.Transaction import Transaction
from model.blockchain.UTXO import UTXO
from model.contracts.CrowdsaleContract import CrowdsaleContract
from model.proofs.Proof import Proof
from protobuf import rgb_pb2


class CrowdsaleBuyProof(Proof):
    def __init__(self, utxo: UTXO, contract: CrowdsaleContract, outputs: List[RGBOutput], blockchain=None):
        super().__init__(utxo, [], outputs)

        self.contract = contract
        self.blockchain: Blockchain = blockchain

    def serialize_data(self, pb_proof: rgb_pb2.Proof) -> rgb_pb2.Proof:
        crowdsale_buy_proof_data = rgb_pb2.CrowdsaleBuyProofData()
        crowdsale_buy_proof_data.contract.CopyFrom(self.contract.serialize())

        pb_proof.crowdsale_buy_proof_data.CopyFrom(crowdsale_buy_proof_data)

        return pb_proof

    def verify(self) -> bool:
        if not self.utxo.spent:
            raise Exception('Proof committed to unspent UTXO {}'.format(self.utxo))

        # TODO: verify the commitment to this proof

        def get_bought_tokens_and_change(tx: Transaction):
            if len(tx.utxos) != 2:
                raise Exception('Found more than two outputs in a CrowdsaleBuyProof tx')

            # Iterate through all the outputs and accumulate how much has been paid to the
            # crowdsale's deposit address provided in the contract.
            payed_to_crowdsale = 0
            for utxo in tx.utxos:
                if utxo.to == self.contract.deposit_address:
                    payed_to_crowdsale += utxo.amount

            # Calculate how many token has been bought and how many satoshis are left as change
            token_bought = math.floor(payed_to_crowdsale / self.contract.price_sat)

            return token_bought, payed_to_crowdsale - (token_bought * self.contract.price_sat)

        def scan_blocks():
            # Iterate through all the blocks in the range [contract.from_block, contract.to_block]
            # to count how many tokens has been bought.
            remaining_tokens = self.contract.total_supply

            # IMPORTANT NOTE: here we are using the order in which transactions are pushed into a block.
            # This means that transactions pushed before have some kind of priority on transactions pushed
            # later when we have to decide who is going to get the tokens and who is going to get the refund.
            # See https://github.com/BHBNETWORK/RGB/issues/18 to learn more.
            for blocks in self.blockchain.get_range(self.contract.from_block, self.contract.to_block):
                for tx in blocks.get_transaction_to(self.contract.deposit_address):
                    # Reject transactions which don't have exactly two outputs
                    # This is necessary because we have to agree on which output will receive the
                    # newly-bought tokens. With two outputs it's pretty easy:
                    # one is paying to the crowdsale address while the other will receive all the tokens.
                    # Once again, see https://github.com/BHBNETWORK/RGB/issues/18 to learn more.
                    if len(tx.utxos) != 2:
                        continue

                    tokens, change = get_bought_tokens_and_change(tx)

                    # Make sure that we are not exceeding the max supply of tokens. We can buy `remaning_tokens` at most
                    can_buy = min(tokens, remaning_tokens)
                    change += self.contract.price_sat * (tokens - can_buy)

                    if tx.txid == self.utxo.txid:  # our transaction, return how many tokens we can buy
                        return can_buy, change

                    remaining_tokens -= can_buy

        # Check how many tokens we are allowed to buy
        user_token_bought, user_change = scan_blocks()

        # ------------

        require_token_output = user_token_bought > 0
        require_change_output = user_change > 0

        if not require_token_output and not require_change_output:
            raise Exception('No change or token available')

        token_outputs: List[RGBOutput] = []
        change_outputs: List[RGBOutput] = []

        # Iterate the RGBOutput of this proof
        for output in self.outputs:
            if output.token_id == self.contract.get_token_id():
                token_outputs.append(output)
            elif output.token_id == self.contract.get_change_token_id():
                change_outputs.append(output)
            else:
                raise Exception('Output is neither a token or change: {}'.format(output))

        total_token_amount: int = reduce(lambda x, y: x + y.amount, token_outputs, 0)
        total_change_amount: int = reduce(lambda x, y: x + y.amount, change_outputs, 0)

        # ------------

        # Check that everything matches
        if require_token_output:
            if len(token_outputs) == 0:
                raise Exception('Missing token output in CrowdsaleBuyProof committed to {}'.format(self.utxo))
            if total_token_amount != user_token_bought:
                raise Exception(
                    'Invalid token amount (got {}, expected {}) in CrowdsaleBuyProof committed to {}'.format(
                        total_token_amount, user_token_bought, self.utxo))

        if require_change_output:
            if len(change_outputs) == 0:
                raise Exception('Missing change output in CrowdsaleBuyProof committed to {}'.format(self.utxo))
            if total_change_amount != user_change:
                raise Exception(
                    'Invalid change amount (got {}, expected {}) in CrowdsaleBuyProof committed to {}'.format(
                        total_change_amount, user_change, self.utxo))

        # Make sure that:
        # - The contract is valid
        # - We have no inputs
        # - The transaction committing to this proof has been confirmed within the range of blocks specified in the contract

        return self.contract.verify() and \
               len(self.inputs_proof) == 0 and \
               self.contract.from_block <= self.utxo.transaction.block.height <= self.contract.to_block
