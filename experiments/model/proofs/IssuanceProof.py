from model.Contract import Contract
from model.RGBOutput import RGBOutput
from model.UTXO import UTXO
from model.proofs.Proof import Proof


class IssuanceProof(Proof):
    def __init__(self, utxo: UTXO, contract: Contract):
        super().__init__(utxo, [], [RGBOutput(contract.get_token_id(), contract.total_supply, contract.owner_utxo)])

        assert contract.issuance_utxo == utxo, "Invalid issuance proof"

        self.contract = contract

    def verify(self) -> bool:
        # Make sure that:
        # - The contract is valid
        # - The contract issuance utxo matches this proof's one
        # - The proof has no inputs
        # - The proof has only one output
        # - The only output matches the token id from the contract
        # - The only output is sent to the 'owner_utxo'
        # - The amount sent matches the total_supply from the contract

        return self.contract.verify() and \
               self.contract.issuance_utxo == self.utxo and \
               len(self.inputs_proof) == 0 and \
               len(self.outputs) == 1 and \
               self.outputs[0].token_id == self.contract.get_token_id() and \
               self.outputs[0].to == self.contract.owner_utxo and \
               self.outputs[0].amount == self.contract.total_supply
