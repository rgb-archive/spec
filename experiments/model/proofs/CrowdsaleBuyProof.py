import math

from model.RGBOutput import RGBOutput
from model.UTXO import UTXO
from model.blockchain.Blockchain import Blockchain
from model.blockchain.Transaction import Transaction
from model.contracts.CrowdsaleContract import CrowdsaleContract
from model.proofs.Proof import Proof


class CrowdsaleBuyProof(Proof):
    def __init__(self, utxo: UTXO, contract: CrowdsaleContract, token_amount: int, change_amount: int, to_utxo: UTXO,
                 change_to_utxo: UTXO, blockchain: Blockchain):
        assert token_amount > 0 or change_amount > 0, "Invalid amounts"

        rgb_outputs = []

        if token_amount > 0:
            rgb_outputs.append(RGBOutput(contract.get_token_id(), token_amount, to_utxo))

        if change_amount > 0:
            rgb_outputs.append(RGBOutput(contract.get_change_token_id(), change_amount, change_to_utxo))

        super().__init__(utxo, [], rgb_outputs)

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

        # FIXME
        if len(self.outputs) > 2 or (len(self.outputs) == 2 and self.outputs[0].token_id == self.outputs[1].token_id):
            return False  # Remove this check by aggregating multiple token outputs or change outputs

        token_output = [o for o in self.outputs if o.token_id == self.contract.get_token_id()]
        change_output = [o for o in self.outputs if o.token_id == self.contract.get_change_token_id()]

        if require_token_output:
            if len(token_output) == 0:
                return False  # no token output
            if token_output[0].amount != user_token_bought:
                return False  # invalid amount

        if require_change_output:
            if len(change_output) == 0:
                return False  # no change output
            if change_output[0].amount != user_change:
                return False  # invalid amount

        return self.contract.verify() and \
               len(self.inputs_proof) == 0 and \
               self.contract.from_block <= self.utxo.transaction.block.height <= self.contract.to_block
