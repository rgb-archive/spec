from model.Contract import Contract
from model.RGBOutput import RGBOutput
from model.UTXO import UTXO
from model.proofs.Proof import Proof


class IssuanceProof(Proof):
    def __init__(self, utxo: UTXO, contract: Contract):
        super().__init__(utxo, [], [RGBOutput(contract.get_token_id(), contract.total_supply, contract.owner_utxo)])

        assert contract.issuance_utxo == utxo, "Invalid issuance proof"

        self.contract = contract
