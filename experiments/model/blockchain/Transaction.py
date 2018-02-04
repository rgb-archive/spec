from typing import List, Dict

from model.blockchain.Block import Block


class Transaction:
    def __init__(self, txid: str, map_amounts: Dict[str, int]):
        from model.UTXO import UTXO

        assert len(map_amounts.keys()) > 0, "Transaction with no output"

        self.txid = txid
        self.map_amounts = map_amounts

        self.utxos: List[UTXO] = []
        self.block: Block or None = None

        for address, count in zip(map_amounts, range(len(map_amounts.keys()))):
            self.utxos.append(UTXO(txid, count, address, map_amounts[address]))

    def get_utxo(self, index: int):
        assert index < len(self.utxos), "Index out of range"

        return self.utxos[index]

    def set_block(self, block: Block):
        self.block = block

    def __str__(self):
        return 'TX {}, Block {}, utxos: \n' \
               '{}'.format(self.txid, self.block, self.utxos)
