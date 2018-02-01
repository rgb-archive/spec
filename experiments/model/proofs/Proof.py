from typing import List

from model import UTXO
from model.RGBOutput import RGBOutput


class Proof:
    def __init__(self, utxo: UTXO, inputs_proof: List['Proof'], outputs: List[RGBOutput]):
        self.utxo = utxo
        self.inputs_proof = inputs_proof
        self.outputs = outputs
