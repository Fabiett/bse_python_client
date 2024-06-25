import gql

class BseIdObject:
    def __init__(self, id: int, bse_gql: gql.Client):
        self.id = id
        self.gql_connection = bse_gql