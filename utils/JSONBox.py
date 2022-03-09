import pprint
import json


class JSONBox:
    
    
    def __init__(self, json_string=None):
        if json_string is not None:
            if isinstance(json_string, dict):
                self.json = json_string
            else:
                self.json = json.loads(json_string)
        else:
            self.json = {}


    def __str__(self):
        return pprint.pformat(self.json, indent=2)
    
    
    def __getitem__(self, path):
        tmp = self.json
        for nm in path.split('.'):
            if isinstance(tmp, list):
                try:
                    tmp = tmp[int(nm)]
                except (ValueError, IndexError):
                    return None
            elif isinstance(tmp, dict):
                try:
                    tmp = tmp[nm]
                except KeyError:
                    return None
            else:
                return None
        return tmp


    def __setitem__(self, path, val):
        path = path.split('.')
        tmp = self.json
        for nm in path[:-1]:
            if isinstance(tmp, list):
                tmp = tmp[int(nm)]
            elif isinstance(tmp, dict):
                try:
                    tmp = tmp[nm]
                except KeyError:
                    tmp[nm] = {}
                    tmp = tmp[nm]
            else:
                raise ValueError(f'Path to value {path}')

        if isinstance(tmp, list):
            tmp[int(path[-1])] = val 
        elif isinstance(tmp, dict):
            tmp[path[-1]] = val
        else:
            raise ValueError('Unknown element')
    