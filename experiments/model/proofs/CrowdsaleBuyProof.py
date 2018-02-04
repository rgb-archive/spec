import math

from model.RGBOutput import RGBOutput
from model.UTXO import UTXO
from model.contracts.CrowdsaleContract import CrowdsaleContract
from model.proofs.Proof import Proof


class CrowdsaleBuyProof(Proof):
    def __init__(self, utxo: UTXO, contract: CrowdsaleContract, amount: int, to_utxo: UTXO):
        assert amount > 0, "Invalid token amount"

        super().__init__(utxo, [], [RGBOutput(contract.get_token_id(), amount, to_utxo)])

        self.contract = contract

    def verify(self) -> bool:
        if not self.utxo.spent:
            raise Exception('Proof committed to unspent UTXO {}'.format(self.utxo))

        # Make sure that:
        # - The contract is valid
        # - The proof has no inputs
        # - The proof has only one output. FIXME
        # - The only output matches the token id from the contract

        payed_to_crowdsale = 0
        for utxo in self.utxo.transaction.utxos:
            if utxo.to == self.contract.deposit_address:
                payed_to_crowdsale += utxo.amount

        token_bought = math.floor(payed_to_crowdsale / self.contract.price_sat)

        return self.contract.verify() and \
               len(self.inputs_proof) == 0 and \
               len(self.outputs) == 1 and \
               self.outputs[0].token_id == self.contract.get_token_id() and \
               self.outputs[0].amount == token_bought and \
               self.contract.from_block <= self.utxo.transaction.block.height <= self.contract.to_block
