from typing import List, Union

import gql
from cachetools.func import ttl_cache
from gql import dsl
from gql.transport.httpx import HTTPXAsyncTransport

from bse.schema import ds
from bse.structures.folder import Folder
from bse.structures.site import Site
from bse.utils import InstanceRegistry, RecrNameSpace

# TODO: Add mutations to add / delete a site


class BseServerQueries:

    @ttl_cache(ttl=1)
    @staticmethod
    def site_tree(gql_connection: gql.Client) -> dict:
        query = dsl.dsl_gql(
            dsl.DSLQuery(
                ds.Query.site_tree.select(
                    ds.SiteTree.sites.select(
                        ds.Site.id, ds.Site.name, ds.Site.parent_id
                    ),
                    ds.SiteTree.folders.select(
                        ds.Folder.id, ds.Folder.name, ds.Folder.parent_id
                    ),
                )
            )
        )

        return gql_connection.execute(query)


class BseServer:
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        ssl_verify: bool = True,
        ssl_keep_insecure_warnings: bool = True,
        name: str = None,
    ):

        self.endpoint = endpoint
        self.name = name

        gql_client_headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        gql_client_transport = HTTPXAsyncTransport(
            url=endpoint, headers=gql_client_headers, verify=ssl_verify
        )

        self.gql_connection = gql.Client(
            transport=gql_client_transport,
            fetch_schema_from_transport=True,
        )

        if ssl_keep_insecure_warnings is not True:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def __repr__(self):
        return f'{self.__class__.__name__}(endpoint: "{self.endpoint}", name: "{self.name}")'

    @property
    def site_tree(self) -> List[Union["Folder", "Site"]]:
        gql_response = RecrNameSpace(BseServerQueries.site_tree(self.gql_connection))

        self._site_tree = [
            InstanceRegistry.get_instance(Folder, folder.id, self.gql_connection)
            for folder in gql_response.site_tree.folders
        ]
        self._site_tree += [
            InstanceRegistry.get_instance(Site, site.id, self.gql_connection)
            for site in gql_response.site_tree.sites
        ]

        return self._site_tree
