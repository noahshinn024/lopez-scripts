"""
Grabs NAC data from MECI interpolation results.

Example run:
>>> python extract_nac_data.py reactant_dir product_dir write.json 6

"""

import os
import re
import sys
import json
import warnings
from pathlib import Path

from typing import List, NamedTuple

assert len(sys.argv) == 5
REACTANT_DIR = sys.argv[1]
PRODUCT_DIR = sys.argv[2]
WRITE_FILE = sys.argv[3]
NATOMS = int(sys.argv[4])


class NACData(NamedTuple):
    atom_types: List[List[str]]
    coords: List[List[List[float]]]
    energy_differences: List[float]
    nacs: List[List[List[float]]]

def extract_data_from_meci_logs(reactant_dir: str, product_dir: str, write_file: str, natoms: int) -> None:
    data = {} 
    species = []
    coords = []
    energy_differences = []
    nacs = []

    log_filepaths = []
    
    def get_log_filenames(root_dir: str) -> List[str]:
        filenames = []
        for path in Path(root_dir).rglob('*.log'):
            filenames += [path]
        return filenames

    log_filepaths += get_log_filenames(reactant_dir)
    log_filepaths += get_log_filenames(product_dir)

    for i, file in enumerate(log_filepaths):
        species_, coords_, energy_differences_, nacs_ = extract_data_from_file(file, natoms)        
        species += species_
        coords += coords_ 
        energy_differences += energy_differences_ 
        nacs += nacs_ 
        print(f'extracted data from file #{i + 1}: {file}')

    data['species'] = species
    data['coords'] = coords 
    data['e_diffs'] = energy_differences
    data['nacs'] = nacs

    with open(write_file, 'w') as f:
        json.dump(data, f)
    print(f'successfully extracted data to `{write_file}`')
    print(f'size: {os.path.getsize(write_file)}')
        
def extract_data_from_file(data_file: str, natoms: int) -> NACData:
    with open(data_file) as f:
        raw_data = f.readlines()
        if is_happy_landing(raw_data):
            species = []
            coords = []
            energy_differences = []
            nacs = []
            for i, line in enumerate(raw_data):
                if 'Total derivative coupling' in line:
                    nac = []
                    for j in range(8, 8 + natoms):
                        match_number = re.compile(r'-?\ *[0-9]+\.?[0-9]*(?:[Ee]\ *-?\ *[0-9]+)?')
                        atom_nac = [float(x) for x in re.findall(match_number, raw_data[i+j])][1:]
                        nac += [atom_nac]
                    nacs += [nac]

                    coord_keyword_idx = get_last_instance_idx('Cartesian coordinates in Angstrom', raw_data)
                    single_molecule_atom_types = []
                    single_molecule_coords = []
                    for j in range(coord_keyword_idx + 4, coord_keyword_idx + 4 + natoms):
                        split = raw_data[j].split()
                        atom_type = split[1][0]
                        coord = [float(i) for i in split[2:]]
                        single_molecule_atom_types += [atom_type]
                        single_molecule_coords += [coord]
                    species += [single_molecule_atom_types]
                    coords += [single_molecule_coords]

                    energy_difference = float(raw_data[i - 4].split('Energy difference: ')[1].replace('\n', ''))
                    energy_differences += [energy_difference]
                    break
        else:
            warnings.warn(f'{data_file} is not valid')
            return [], [], [], [], [] # type: ignore

    print(species)
    print(coords)
    print(energy_differences)
    print(nacs)
    assert len(species) == len(coords) == len(energy_differences) == len(nacs)
    return NACData(species, coords, energy_differences, nacs)

def get_last_instance_idx(keyword: str, data: List[str]) -> int:
    cur_idx = 0
    for i, line in enumerate(data):
        if keyword in line:
            cur_idx = max(i, cur_idx)
    return cur_idx

def is_happy_landing(raw_data: List) -> bool:
    return 'Happy landing!' in raw_data[-4]


if __name__ == '__main__':
    extract_data_from_meci_logs(REACTANT_DIR, PRODUCT_DIR, WRITE_FILE, NATOMS)
