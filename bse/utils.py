import json
from types import SimpleNamespace

import gql

# Kind of copied it from this -> https://dev.to/taqkarim/extending-simplenamespace-for-nested-dictionaries-58e8#comment-11p5l
RecrNameSpace = lambda serializable_dict: json.loads(
    json.dumps(serializable_dict), object_hook=lambda item: SimpleNamespace(**item)
)


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
