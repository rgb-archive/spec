from typing import Dict

from model.blockchain.Transaction import Transaction


class UTXO:
    def __init__(self, txid: str or None, index: int, to: str or None = None, amount: int or None = None,
                 spent: bool = False, transaction: Transaction or None = None):
        assert index >= 0, "The UTXO index must be positive"
        assert to != '', "Invalid destination address"
        assert amount is None or amount > 0, "Invalid UTXO amount"

        if txid == '':
            txid = None

        self.txid = txid
        self.index = index
        self.to = to
        self.amount = amount
        self.spent = spent
        self.transaction = transaction

    def known_txid(self) -> bool:
        return self.txid is not None

    def spend(self):
        if self.spent:
            raise Exception('UTXO {} has already been spent'.format(self))

        self.spent = True

    def set_transaction(self, transaction: Transaction):
        self.transaction = transaction

    @staticmethod
    def from_string(string: str) -> 'UTXO':
        parts = string.split(':')
        return UTXO(parts[0] if parts[0] != '' else None, int(parts[1]))

    @staticmethod
    def from_dict(in_dict):
        return UTXO(in_dict['txid'], in_dict['index'], in_dict['to'], in_dict['amount'])

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.txid == other.txid and self.index == other.index and self.to == other.to and self.amount == other.amount

        return False

    def __str__(self) -> str:
        return 'UTXO<{}:{}> {} SAT -> {}'.format(self.txid, self.index, self.amount, self.to)

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> Dict[str, str or int]:
        return {
            'txid': self.txid,
            'index': self.index,
            'to': self.to,
            'amount': self.amount
        }
