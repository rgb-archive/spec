from model.blockchain.UTXO import UTXO
from model.contracts.AbstractContract import AbstractContract
from protobuf import rgb_pb2


class Contract(AbstractContract):
    def __init__(self, title: str, issuance_utxo: UTXO, owner_utxo: UTXO, total_supply: int):
        super().__init__(title, issuance_utxo, total_supply)

        self.owner_utxo = owner_utxo

    def get_type(self) -> str:
        return 'generic_contract'

    @staticmethod
    def deserialize(pb_contract: rgb_pb2.Contract) -> 'Contract':
        return Contract(pb_contract.title, UTXO.deserialize(pb_contract.issuance_utxo),
                        UTXO.deserialize(pb_contract.owner_utxo), pb_contract.total_supply)

    def serialize(self) -> rgb_pb2.Contract:
        contract = rgb_pb2.Contract()

        contract.title = self.title
        contract.type = self.get_type()
        contract.issuance_utxo.CopyFrom(self.issuance_utxo.serialize())
        contract.owner_utxo.CopyFrom(self.owner_utxo.serialize())
        contract.total_supply = self.total_supply

        return contract
