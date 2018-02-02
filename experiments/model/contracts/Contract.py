import json
from typing import Dict

from model.UTXO import UTXO
from model.contracts.AbstractContract import AbstractContract


class Contract(AbstractContract):
    def __init__(self, title: str, issuance_utxo: UTXO, owner_utxo: UTXO, total_supply: int):
        super().__init__(title, issuance_utxo, total_supply)

        self.owner_utxo = owner_utxo

    def get_type(self) -> str:
        return 'generic_contract'

    @staticmethod
    def from_json_obj(obj: Dict) -> 'Contract':
        issuance_utxo = UTXO.from_dict(obj['issuance_utxo'])
        owner_utxo = UTXO.from_dict(obj['owner_utxo'])

        return Contract(obj['title'], issuance_utxo, owner_utxo, obj['total_supply'])

    def to_json(self) -> str:
        return json.dumps({
            'title': self.title,
            'issuance_utxo': self.issuance_utxo.to_dict(),
            'owner_utxo': self.owner_utxo.to_dict(),
            'total_supply': self.total_supply
        }, sort_keys=True)

    def verify(self) -> bool:
        # TODO: verify the commitment on the blockchain

        return self.issuance_utxo.spent
