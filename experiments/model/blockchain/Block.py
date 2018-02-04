from typing import List


class Block:
    def __init__(self, height: int, transactions: List):
        from model.blockchain.Transaction import Transaction

        assert height > 0, "Invalid block height"

        self.height = height
        self.transactions: List[Transaction] = transactions

        for tx in self.transactions:
            tx.set_block(self)

    def __str__(self):
        return 'Block<{}>'.format(self.height)
