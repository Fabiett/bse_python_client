from importlib import resources
import gql

# Import of the static schema -> TODO: Thing about how to update the schema for every version
bse_schema_file = resources.files() / "bse_schema.gql"

with open(bse_schema_file) as fp:
    gql_schema = fp.read()

client = gql.Client(gql_schema)
ds = gql.dsl.DSLSchema(client.schema)