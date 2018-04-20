from model.blockchain.UTXO import UTXO
from protobuf import rgb_pb2


class RGBOutput:
    def __init__(self, token_id: str, amount: int, to: UTXO):
        assert amount > 0, "Amount must be > 0"
        assert amount < 2 ** 64, "Amount must be <= 2^64 - 1"

        self.token_id = token_id
        self.amount = amount
        self.to = to

    def __str__(self) -> str:
        return 'RGBOutput of token {}. Moving {} to {}'.format(self.token_id, self.amount, self.to)

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def deserialize(pb_rgb_output: rgb_pb2.RGBOutput) -> 'RGBOutput':
        return RGBOutput(pb_rgb_output.token_id,
                         pb_rgb_output.amount,
                         UTXO.deserialize(pb_rgb_output.to))

    def serialize(self) -> rgb_pb2.RGBOutput:
        pb_output = rgb_pb2.RGBOutput()

        pb_output.token_id = self.token_id
        pb_output.amount = self.amount
        pb_output.to.CopyFrom(self.to.serialize())

        return pb_output
