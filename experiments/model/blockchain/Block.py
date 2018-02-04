from typing import List


class Block:
    def __init__(self, height: int, transactions: List, blockchain):
        from model.blockchain.Transaction import Transaction

        assert height > 0, "Invalid block height"

        self.height = height
        self.transactions: List[Transaction] = transactions

        for tx in self.transactions:
            tx.set_block(self)

        blockchain.add_block(self)

    def get_transaction_to(self, address: str):
        from model.blockchain.Transaction import Transaction

        return_list: List[Transaction] = []

        def check_outputs(tx: Transaction):
            for output in tx.utxos:
                if output.to == address:
                    return return_list.append(tx)

        for tx in self.transactions:
            check_outputs(tx)

        return return_list

    def __str__(self):
        return 'Block<{}>'.format(self.height)
