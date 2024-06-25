from typing import List, Union

import gql
from cachetools.func import ttl_cache
from gql import dsl

from bse.schema import ds
from bse.structures.bseidobject import BseIdObject
from bse.structures.extensions import Extension
from bse.structures.scanconfiguration import ScanConfiguration
from bse.structures.site import Site
from bse.utils import InstanceRegistry, RecrNameSpace


class FolderQueries:

    @ttl_cache(ttl=1)
    @property
    def name(folder_id: int, gql_connection: gql.Client) -> dict:
        query = dsl.dsl_gql(
            dsl.DSLQuery(ds.Query.folder(id=folder_id).select(ds.Folder.name))
        )

        return gql_connection.execute(query)

    @ttl_cache(ttl=1)
    @property
    def parent_folder(folder_id: int, gql_connection: gql.Client) -> dict:
        query = dsl.dsl_gql(
            dsl.DSLQuery(ds.Query.folder(id=folder_id).select(ds.Folder.parent_id))
        )

        return gql_connection.execute(query)

    @ttl_cache(ttl=1)
    @staticmethod
    def content(folder_id: int, gql_connection: gql.Client) -> dict:
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

    @ttl_cache(ttl=1)
    @staticmethod
    def scan_configurations(folder_id: int, gql_connection: gql.Client) -> dict:
        query = dsl.dsl_gql(
            dsl.DSLQuery(
                ds.Query.folder(id=folder_id).select(
                    ds.Folder.scan_configurations.select(ds.ScanConfiguration.id)
                )
            )
        )

        return gql_connection.execute(query)
    
class FolderNotImplemented:
    @property
    def email_recipients(self):
        # Rn I don't really care to implement this functionality
        raise NotImplementedError

    @property
    def slack_channels(self):
        # Rn I don't really care to implement this functionality
        raise NotImplementedError

    @property
    def extensions(self) -> List["Extension"]:
        # TODO: Implement Extension first, then this one
        raise NotImplementedError


class Folder(BseIdObject, FolderNotImplemented):

    def __repr__(self):
        return f'{self.__class__.__name__}(name: "{self.name}", id: {self.id})'

    @property
    def name(self):
        gql_response = RecrNameSpace(FolderQueries.name(self.id, self.gql_connection))
        self._name: str = gql_response.folder.name
        return self._name

    @property
    def content(self) -> List[Union["Folder", "Site"]]:
        gql_response = RecrNameSpace(
            FolderQueries.content(self.id, self.gql_connection)
        )

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
        return self._content

    # TODO: test parent directory on the root dir

    @property
    def parent_directory(self) -> "Folder":
        gql_response = RecrNameSpace(
            FolderQueries.parent_folder(self.id, self.gql_connection)
        )

        self._parent_directory: Folder = InstanceRegistry(
            Folder, gql_response.folder.parent_id
        )
        return self._parent_directory

    @property
    def scan_configurations(self) -> List["ScanConfiguration"]:
        gql_response = RecrNameSpace(
            FolderQueries.scan_configurations(self.id, self.gql_connection)
        )

        self._scan_configurations: List["ScanConfiguration"] = [
            InstanceRegistry(ScanConfiguration, gql_response.folder.parent_id)
            for scan_configuration in gql_response.folder.scan_configurations
        ]
        return self._scan_configurations