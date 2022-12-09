"""
Merges two json files. The two files must contain the same keys and follow the following format: { key: <list of values> }.

Example run:
>>> python3 merge_json_files.py file1.json file2.json merged.json

"""

import sys
import json

assert len(sys.argv) == 4
JSON_FILE1 = sys.argv[1]
JSON_FILE2 = sys.argv[2]
WRITE_FILENAME = sys.argv[3]


def merge_json_files(f1: str, f2: str, wf: str) -> None:
    with open(f1) as f:
        data1 = json.load(f)
    with open(f2) as f:
        data2 = json.load(f)

    if data1.keys() != data2.keys():
        raise KeyError(f'file1 contains keys {data1.keys()} but file2 contains keys {data2.keys()}')

    merged_data = {}
    for k in data1.keys():
        merged_data[k] = data1[k] + data2[k]

    with open(wf, 'w') as f:
        json.dump(merged_data, f)
        print(f'merged {f1.split(".")[-1]} with {f2.split(".")[-1]} into {wf.split(".")[-1]}')


if __name__ == '__main__':
    merge_json_files(JSON_FILE1, JSON_FILE2, WRITE_FILENAME)
