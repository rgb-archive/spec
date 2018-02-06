import math
from functools import reduce
from typing import List

from model.RGBOutput import RGBOutput
from model.UTXO import UTXO
from model.blockchain.Blockchain import Blockchain
from model.blockchain.Transaction import Transaction
from model.contracts.CrowdsaleContract import CrowdsaleContract
from model.proofs.Proof import Proof


class CrowdsaleBuyProof(Proof):
    def __init__(self, utxo: UTXO, contract: CrowdsaleContract, outputs: List[RGBOutput], blockchain: Blockchain):
        super().__init__(utxo, [], outputs)

        self.contract = contract
        self.blockchain = blockchain

    def verify(self) -> bool:
        if not self.utxo.spent:
            raise Exception('Proof committed to unspent UTXO {}'.format(self.utxo))

        # Make sure that:
        # - The contract is valid
        # - The proof has no inputs
        # - The proof has only one output. FIXME
        # - The only output matches the token id from the contract

        def get_bought_tokens_and_change(tx: Transaction):
            payed_to_crowdsale = 0
            for utxo in tx.utxos:
                if utxo.to == self.contract.deposit_address:
                    payed_to_crowdsale += utxo.amount

            token_bought = math.floor(payed_to_crowdsale / self.contract.price_sat)

            return token_bought, payed_to_crowdsale - (token_bought * self.contract.price_sat)

        def scan_blocks():
            remaining_tokens = self.contract.total_supply

            for blocks in self.blockchain.get_range(self.contract.from_block, self.contract.to_block):
                for tx in blocks.get_transaction_to(self.contract.deposit_address):
                    tokens, change = get_bought_tokens_and_change(tx)

                    can_buy = tokens if tokens < remaining_tokens else remaining_tokens
                    change += self.contract.price_sat * (tokens - can_buy)

                    if tx.txid == self.utxo.txid:  # our transaction
                        return can_buy, change

                    remaining_tokens -= can_buy

        user_token_bought, user_change = scan_blocks()

        # ------------

        require_token_output = user_token_bought > 0
        require_change_output = user_change > 0

        if not require_token_output and not require_change_output:
            raise Exception('No change or token available')

        token_outputs: List[RGBOutput] = []
        change_outputs: List[RGBOutput] = []

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

        return self.contract.verify() and \
               len(self.inputs_proof) == 0 and \
               self.contract.from_block <= self.utxo.transaction.block.height <= self.contract.to_block
