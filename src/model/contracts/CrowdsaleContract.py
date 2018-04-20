import hashlib

from model.blockchain.UTXO import UTXO
from model.contracts.AbstractContract import AbstractContract
from protobuf import rgb_pb2


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

    def get_change_token_id(self) -> str:
        hash_object = hashlib.sha256(('CHANGE'.encode('ascii') + self.serialize_to_string()))
        return hash_object.hexdigest()

    @staticmethod
    def deserialize(pb_contract: rgb_pb2.Contract) -> 'CrowdsaleContract':
        return CrowdsaleContract(pb_contract.title, UTXO.deserialize(pb_contract.issuance_utxo),
                                 pb_contract.total_supply, pb_contract.price_sat, pb_contract.from_block,
                                 pb_contract.to_block, pb_contract.deposit_address)

    def serialize(self) -> rgb_pb2.Contract:
        contract = rgb_pb2.Contract()

        contract.title = self.title
        contract.type = self.get_type()
        contract.issuance_utxo.CopyFrom(self.issuance_utxo.serialize())
        contract.total_supply = self.total_supply
        contract.price_sat = self.price_sat
        contract.from_block = self.from_block
        contract.to_block = self.to_block
        contract.deposit_address = self.deposit_address

        return contract

    def __str__(self):
        return 'Contract (type="{}") "{}", token id = {}, change token id = {}\n' \
               'Committed to UTXO {}\n' \
               'Total issuance of {}'.format(self.title, self.get_type(), self.get_token_id(),
                                             self.get_change_token_id(),
                                             self.issuance_utxo, self.total_supply)
