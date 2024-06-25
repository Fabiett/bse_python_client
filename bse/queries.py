from . import schema

from gql import dsl, Client
from importlib import resources

from typing import overload


bse_schema_file = resources.files(schema) / "bse_schema.gql"

with open(bse_schema_file) as fp:
    gql_schema = fp.read()

client = Client(gql_schema)
ds = dsl.DSLSchema(client.schema)


def executable_query_out(function):
    """Needed to convert functions that return dsl.DSLQuery
    to function that return gql.DocuentNode"""

    def wrapper(*args, **kwargs):
        return dsl.dsl_gql(function(*args, **kwargs))

    return wrapper


folder_tree = dsl.dsl_gql(
    dsl.DSLQuery(
        ds.Query.site_tree.select(
            ds.SiteTree.sites.select(ds.Site.id, ds.Site.name, ds.Site.parent_id),
            ds.SiteTree.folders.select(
                ds.Folder.id, ds.Folder.name, ds.Folder.parent_id
            ),
        )
    )
)


@executable_query_out
def _site_query(site_id: str) -> dsl.DSLQuery:
    return dsl.DSLQuery(
        ds.Query.site(id=site_id).select(
            ds.Site.name,
            ds.Site.scope_v2.select(
                ds.ScopeV2.start_urls,
                ds.ScopeV2.in_scope_url_prefixes,
                ds.ScopeV2.out_of_scope_url_prefixes,
                ds.ScopeV2.protocol_options,
            ),
            ds.Site.scan_configurations.select(ds.ScanConfiguration.id),
        )
    )


@overload
def site(site_id: str) -> dsl.DSLQuery:
    if not site_id.isdigit():
        raise TypeError
    return _site_query(site_id)


def site(site_id: int) -> dsl.DSLQuery:
    return _site_query(str(site_id))
