from typing import List

from model import UTXO
from model.RGBOutput import RGBOutput


class Proof:
    def __init__(self, utxo: UTXO, inputs_proof: List['Proof'], outputs: List[RGBOutput]):
        assert utxo.known_txid(), "Cannot commit to an unknown UTXO"

        self.utxo = utxo
        self.inputs_proof = inputs_proof
        self.outputs = outputs

    def __str__(self) -> str:
        return 'Proof committed to {}\n' \
               'Inputs: {}\n' \
               'Outputs: {}'.format(self.utxo, self.inputs_proof, self.outputs)

    def __repr__(self) -> str:
        return 'Proof committed to {}'.format(self.utxo)
