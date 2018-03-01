import hashlib
import json
from typing import Dict

from model.UTXO import UTXO
from model.contracts.AbstractContract import AbstractContract


class CrowdsaleContract(AbstractContract):
    def __init__(self, title: str, issuance_utxo: UTXO, total_supply: int, price_sat: int, from_block: int,
                 to_block: int, deposit_address: str):
        super().__init__(title, issuance_utxo, total_supply)

        assert from_block > 0, "Block must be > 0"
        assert to_block > from_block, "to_block must be > from_block"
        assert price_sat > 0, "Price must be > 0"

        self.from_block = from_block
        self.to_block = to_block
        self.price_sat = price_sat
        self.deposit_address = deposit_address

    def get_type(self) -> str:
        return 'crowdsale_contract'

    @staticmethod
    def from_json_obj(obj: Dict) -> 'CrowdsaleContract':
        issuance_utxo = UTXO.from_dict(obj['issuance_utxo'])

        return CrowdsaleContract(obj['title'], issuance_utxo, obj['total_supply'], obj['price_sat'], obj['from_block'],
                                 obj['to_block'], obj['deposit_address'])

    def get_change_token_id(self) -> str:
        hash_object = hashlib.sha256((self.to_json() + 'CHANGE').encode('utf-8'))
        return hash_object.hexdigest()

    def to_json(self) -> str:
        return json.dumps({
            'title': self.title,
            'type': self.get_type(),
            'issuance_utxo': self.issuance_utxo.to_dict(),
            'total_supply': self.total_supply,
            'from_block': self.from_block,
            'to_block': self.to_block,
            'price_sat': self.price_sat,
            'deposit_address': self.deposit_address
        }, sort_keys=True)
