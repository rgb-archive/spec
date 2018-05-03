from typing import List, Dict

from model.RGBOutput import RGBOutput
from model.blockchain.UTXO import UTXO
from protobuf import rgb_pb2


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

        # Apparently this is safe: https://docs.python.org/3/library/stdtypes.html#dict.values
        if in_amounts != out_amounts:
            raise Exception('Mismatch between input amounts and output amounts: \n'
                            'IN:  {}\n'
                            'OUT: {}'.format(in_amounts, out_amounts))

        return True

    @staticmethod
    def deserialize(pb_proof: rgb_pb2.Proof) -> 'Proof':
        def get_outputs() -> List[RGBOutput]:
            return [RGBOutput.deserialize(pb_rgb_out) for pb_rgb_out in pb_proof.outputs]

        def get_inputs() -> List[Proof]:
            return [Proof.deserialize(pb_rgb_in) for pb_rgb_in in pb_proof.inputs]

        if pb_proof.HasField("issuance_proof_data"):
            from model.proofs.IssuanceProof import IssuanceProof
            from model.contracts.Contract import Contract

            return IssuanceProof(
                UTXO.deserialize(pb_proof.utxo),
                Contract.deserialize(pb_proof.issuance_proof_data.contract)
            )

        if pb_proof.HasField("crowdsale_buy_proof_data"):
            from model.proofs.CrowdsaleBuyProof import CrowdsaleBuyProof
            from model.contracts.CrowdsaleContract import CrowdsaleContract

            return CrowdsaleBuyProof(
                UTXO.deserialize(pb_proof.utxo),
                CrowdsaleContract.deserialize(pb_proof.crowdsale_buy_proof_data.contract),
                get_outputs(),
                None
            )

        return Proof(UTXO.deserialize(pb_proof.utxo), get_inputs(), get_outputs())

    def serialize(self, skip_inputs=False):
        proof = rgb_pb2.Proof()

        proof.utxo.CopyFrom(self.utxo.serialize())

        if not skip_inputs:
            for proof_input in self.inputs_proof:
                pb_input = proof.inputs.add()
                pb_input.CopyFrom(proof_input.serialize())

        for proof_output in self.outputs:
            pb_output = proof.outputs.add()
            pb_output.CopyFrom(proof_output.serialize())

        return self.serialize_data(proof)

    @classmethod
    def serialize_data(cls, pb_proof: rgb_pb2.Proof) -> rgb_pb2.Proof:
        return pb_proof

    def __str__(self) -> str:
        return 'Proof committed to {}\n' \
               'Inputs: {}\n' \
               'Outputs: {}'.format(self.utxo, self.inputs_proof, self.outputs)

    def __repr__(self) -> str:
        return 'Proof committed to {}'.format(self.utxo)
