import gql
from gql import dsl

from cachetools.func import ttl_cache

from bse.structures.bseidobject import BseIdObject
from bse.schema import ds

# TODO: test the query, since the fucking company VPN is stuck, as of right now
class ScanConfigurationQueries:
    @ttl_cache(ttl=1)
    @staticmethod
    def scan_configurations(gql_connection: gql.Client) -> dict:
        query = dsl.dsl_gql(
            dsl.DSLQuery(
                ds.Query.scan_configurations.select(
                    ds.ScanConfiguration.id,
                    ds.ScanConfiguration.name,
                    ds.ScanConfiguration.scan_configuration_fragment_json,
                    ds.ScanConfiguration.built_in,
                    ds.ScanConfiguration.last_modified_time,
                    ds.ScanConfiguration.last_modified_by,
                )
            )
        )

        return gql_connection.execute(query)

class ScanConfiguration(BseIdObject):
    # TODO: Implement
    pass