from typing import List


class Block:
    def __init__(self, height: int, transactions: List):
        assert height > 0, "Invalid block height"

        self.height = height
        self.transactions = transactions

    def __str__(self):
        return 'Block<{}>'.format(self.height)
