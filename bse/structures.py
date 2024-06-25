from . import schema

from importlib import resources

from cachetools.func import ttl_cache

import gql
from gql import dsl, Client
from gql.transport.httpx import HTTPXAsyncTransport

from .utils import RecrNameSpace

from urllib import parse

from typing import List, Union

import asyncio

# TODO: Understand how async requests can be implemented in all of this!
import asyncio

# Import of the static schema -> TODO: Thing about how to update the schema for every version
bse_schema_file = resources.files(schema) / "bse_schema.gql"

with open(bse_schema_file) as fp:
    gql_schema = fp.read()

client = Client(gql_schema)
ds = dsl.DSLSchema(client.schema)


# TODO: For all obj classes, create a function for "autodestruction"
# TODO: Implement __str__ and __repr__ for all classes


class InstanceRegistry:
    _instances = {}

    @classmethod
    def get_instance(
        cls, class_type, id: int, gql_connection: gql.Client, *args, **kwargs
    ):
        # Controlla se esiste già un'istanza con lo stesso ID per la classe specificata
        if (class_type, id, gql_connection) in cls._instances:
            return cls._instances[(class_type, id, gql_connection)]

        # Crea una nuova istanza e memorizzala
        instance = class_type(id, gql_connection, *args, **kwargs)
        cls._instances[(class_type, id, gql_connection)] = instance
        return instance


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

    # TODO: This should return a list of specific Objects (not nested)
    @property
    def site_tree(self) -> List[Union["Folder", "Site"]]:
        self._site_tree_query()
        return self._site_tree

    # No ttl for this one
    def _site_tree_query(self):
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

        gql_response = RecrNameSpace(self.gql_connection.execute(query))

        self._site_tree = [
            InstanceRegistry.get_instance(Folder, folder.id, self.gql_connection)
            for folder in gql_response.site_tree.folders
        ]
        # self._site_tree += [
        #     InstanceRegistry.get_instance(Site, site.id, self.gql_connection)
        #     for site in gql_response.site_tree.sites
        # ]
        return

    # TODO: Add functions to insert and delete sites / folders

    def __repr__(self):
        return (
            f'{self.__class__.__name__}(endpoint: "{self.endpoint}", name: {self.name})'
        )


class BseIdObject:
    def __init__(self, id: int, bse_gql: gql.Client):
        self.id = id
        self.gql_connection = bse_gql


class Folder(BseIdObject):
    @property
    def name(self):
        self._name_query()
        return self._name

    @property
    def extensions(self) -> List["Extension"]:
        raise NotImplementedError

    @property
    def content(self) -> List[Union["Folder", "Site"]]:
        self._content_query()
        return self._content

    @property
    def parent_directory(self) -> "Folder":
        self._parent_directory_query()
        return self._parent_directory

    @property
    def scan_configurations(self) -> List["ScanConfiguration"]:
        raise NotImplementedError

    @property
    def email_recipients(self):
        # Rn I don't really care to implement this functionality
        raise NotImplementedError

    @property
    def slack_channels(self):
        # Rn I don't really care to implement this functionality
        raise NotImplementedError

    @ttl_cache(ttl=1)
    def _name_query(self):
        query = dsl.dsl_gql(
            dsl.DSLQuery(ds.Query.folder(id=self.id).select(ds.Folder.name))
        )

        gql_response = RecrNameSpace(self.gql_connection.execute(query))
        self._name: str = gql_response.folder.name
        return

    @ttl_cache(ttl=1)
    def _parent_directory_query(self):
        query = dsl.dsl_gql(
            dsl.DSLQuery(ds.Query.folder(id=self.id).select(ds.Folder.parent_id))
        )

        gql_response = RecrNameSpace(self.gql_connection.execute(query))

        self._parent_directory: Folder = InstanceRegistry(
            Folder, gql_response.folder.parent_id
        )
        return

    @ttl_cache(ttl=1)
    def _content_query(self):
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

        gql_response = RecrNameSpace(self.gql_connection.execute(query))

        self._content = [
            InstanceRegistry.get_instance(Folder, folder.id, self.gql_connection)
            for folder in gql_response.site_tree.folders
            if folder.parent_id == str(self.id)
        ]
        self._content += [
            InstanceRegistry.get_instance(Site, site.id, self.gql_connection)
            for site in gql_response.site_tree.sites
            if site.parent_id == str(self.id)
        ]
        return

    @ttl_cache(ttl=1)
    def _scan_configurations_query(self):
        query = dsl.dsl_gql(
            dsl.DSLQuery(
                ds.Query.folder(id=self.id).select(
                    ds.Folder.scan_configurations.select(ds.ScanConfiguration.id)
                )
            )
        )

        gql_response = RecrNameSpace(self.gql_connection.execute(query))

        self._scan_configurations: List["ScanConfiguration"] = [
            InstanceRegistry(ScanConfiguration, gql_response.folder.parent_id)
            for scan_configuration in gql_response.folder.scan_configurations
        ]
        return

    def __repr__(self):
        return f'{self.__class__.__name__}(name: "{self.name}", id: {self.id})'


class Site(BseIdObject):
    @property
    def name(self):
        self._basic_info_query()
        return self._name

    @property
    def extensions(self):
        self._basic_info_query()
        return self._extensions

    @property
    def scope(self):
        # TODO: Implement
        raise NotImplemented

    @property
    def scan_configurations(self):
        # TODO: Implement
        raise NotImplemented

    @property
    def parent_directory(self):
        # TODO: Implement
        raise NotImplemented

    @property
    def application_logins(self):
        # TODO: Implement
        raise NotImplemented

    @property
    def settings(self):
        # TODO: Implement
        raise NotImplemented

    @property
    def scans(self):
        # TODO: Implement
        raise NotImplemented

    @ttl_cache(ttl=1)
    def _basic_info_query(self):
        query = dsl.dsl_gql(
            dsl.DSLQuery(
                ds.Query.site(id=self.id).select(
                    ds.Site.name, ds.Site.extensions.select(ds.Extension.id)
                )
            )
        )

        gql_response = RecrNameSpace(self.gql_connection.execute(query))

        self._name = gql_response.site.name
        return

    @ttl_cache(ttl=1)
    def _site_scans_query(self):
        query = dsl.dsl_gql(
            dsl.DSLQuery(ds.Query.scans(site_id=self.id).select(ds.Scan.id))
        )

        gql_response = RecrNameSpace(self.gql_connection.execute(query))

        self._scans = [Scan(scan.id) for scan in gql_response.scans]
        return

    def __repr__(self):
        return f'{self.__class__.__name__}(name: "{self.name}", id: {self.id})'


class Scan(BseIdObject):
    # TODO: Implement
    pass


class Extension(BseIdObject):
    # TODO: Implement
    pass


class ScanConfiguration(BseIdObject):
    # TODO: Implement
    pass
