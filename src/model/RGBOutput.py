from model.UTXO import UTXO


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
