import json
from types import SimpleNamespace

# Kind of copied it from this -> https://dev.to/taqkarim/extending-simplenamespace-for-nested-dictionaries-58e8#comment-11p5l
RecrNameSpace = lambda serializable_dict: json.loads(json.dumps(serializable_dict), object_hook=lambda item: SimpleNamespace(**item))