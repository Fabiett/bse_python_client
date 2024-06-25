import gql
from cachetools.func import ttl_cache
from gql import dsl

from bse.schema import ds
from bse.structures.bseidobject import BseIdObject
from bse.utils import RecrNameSpace


class SiteQueries:

    @ttl_cache(ttl=1)
    @staticmethod
    def name(site_id: int, gql_connection: gql.Client) -> dict:
        query = dsl.dsl_gql(
            dsl.DSLQuery(ds.Query.site(id=site_id).select(ds.Site.name))
        )

        return gql_connection.execute(query)

    @ttl_cache(ttl=1)
    @staticmethod
    def scans(site_id: int, gql_connection: gql.Client) -> dict:
        query = dsl.dsl_gql(
            dsl.DSLQuery(ds.Query.scans(site_id=site_id).select(ds.Scan.id))
        )

        return gql_connection.execute(query)


class SiteNotImplemented:
    @property
    def extensions(self):
        raise NotImplementedError

    @property
    def scope(self):
        # TODO: Implement
        raise NotImplementedError

    @property
    def scan_configurations(self):
        # TODO: Implement
        raise NotImplemented

    @property
    def parent_directory(self):
        # TODO: Implement
        raise NotImplementedError

    @property
    def application_logins(self):
        # TODO: Implement
        raise NotImplementedError

    @property
    def settings(self):
        # TODO: Implement
        raise NotImplementedError

    @property
    def scans(self):
        # TODO: Implement
        raise NotImplementedError


class Site(BseIdObject):

    def __repr__(self):
        return f'{self.__class__.__name__}(name: "{self.name}", id: {self.id})'

    @property
    def name(self):
        query_response = RecrNameSpace(SiteQueries.name(self.id, self.gql_connection))
        self._name = query_response.site.name
        return self._name
