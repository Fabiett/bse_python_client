import bse
from bse import BseServer
from bse.structures.site import Site

from time import perf_counter
from pprint import pprint

from gql import dsl
from typing import overload

import dotenv
envvar = dotenv.dotenv_values()

hawaii_bse = BseServer(
    endpoint=envvar["BSEGRAPHQLENDPOINT"],
    api_key=envvar["BSEAPIKEY"],
    ssl_verify=False,
    ssl_keep_insecure_warnings=False,
    name="My beautifull BSE python Client Server Object"
)

print(hawaii_bse)

x = Site(2, hawaii_bse.gql_connection)