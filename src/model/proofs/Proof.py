from typing import List, Dict

from model import UTXO
from model.RGBOutput import RGBOutput


class Proof:
    def __init__(self, utxo: UTXO, inputs_proof: List['Proof'], outputs: List[RGBOutput]):
        assert utxo.known_txid(), "Cannot commit to an unknown UTXO"

        self.utxo = utxo
        self.inputs_proof = inputs_proof
        self.outputs = outputs

    def verify(self) -> bool:
        if not self.utxo.spent:
            raise Exception('Proof committed to unspent UTXO {}'.format(self.utxo))

        in_amounts: Dict[str, int] = {}
        out_amounts: Dict[str, int] = {}

        # TODO: verify the commitment on the blockchain (from sign-to-contract or in a OP_RETURN output)

        for proof in self.inputs_proof:
            if not proof.verify():
                raise Exception('Invalid input proof from {}'.format(proof.utxo))

            for proof_out in proof.outputs:
                if proof_out.to != self.utxo:
                    continue  # ignore this output, not for us

                in_amounts[proof_out.token_id] = in_amounts.get(proof_out.token_id, 0) + proof_out.amount

        for this_out in self.outputs:
            out_amounts[this_out.token_id] = out_amounts.get(this_out.token_id, 0) + this_out.amount

        if in_amounts != out_amounts:  # FIXME: i have no idea whether this is safe or not in python (comparing dicts)
            raise Exception('Mismatch between input amounts and output amounts: \n'
                            'IN:  {}\n'
                            'OUT: {}'.format(in_amounts, out_amounts))

        return True

    def __str__(self) -> str:
        return 'Proof committed to {}\n' \
               'Inputs: {}\n' \
               'Outputs: {}'.format(self.utxo, self.inputs_proof, self.outputs)

    def __repr__(self) -> str:
        return 'Proof committed to {}'.format(self.utxo)
