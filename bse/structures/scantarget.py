from enum import Enum

import gql

from bse.structures.bseidobject import BseIdObject

class ScanTargetType(Enum):
    site = 1
    cids_site = 2


class ScanTarget(BseIdObject):
    def __init__(
        self,
        id: int,
        name: str,
        type: ScanTargetType,
        ephemeral: bool,
        gql_connection: gql.Client,
    ):
        super().__init__(id, gql_connection=gql_connection)
        self._name = name
        self._type = type
        self._ephemeral = ephemeral

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._ephemeral
