"""
Plots the proportion of hydrogen bonding occurrences at each time step.

To run:
>>> python3 h_bonding_analysis.py root_dir name

"""

import os
import sys
import glob
import matplotlib.pyplot as plt

from typing import List

assert len(sys.argv) == 3
ROOT_DIR = sys.argv[1]
NAME = sys.argv[2]


def run(root_dir: str, name: str) -> None:
    ntraj = len(glob.glob1(ROOT_DIR,"*.dat"))
    last_step_hash: List[int] = []
    largest_step = 0
    for traj_num in range(ntraj):
        file = os.path.join(root_dir, f'{name}-{traj_num}.dat')
        with open(file, 'r') as f:
            cur_largest_step = len(f.readlines())
            last_step_hash.append(cur_largest_step)
            largest_step = max(largest_step, cur_largest_step)

    h_bonding_freq = []
    for step_num in range(largest_step):
        h_bonding_count = 0
        valid_traj_count = 0
        for traj_num in range(ntraj):
            if last_step_hash[traj_num] > step_num:
                valid_traj_count += 1
                file = os.path.join(root_dir, f'{name}-{traj_num}.dat')
                with open(file, 'r') as f:
                    lines = f.readlines() 
                    for l in lines:
                        if l.startswith(f'{step_num} '):
                            num_h_bonding = int(l.split(' ')[-1])
                            if num_h_bonding > 0:
                                h_bonding_count += 1

        h_bonding_freq.append(round(h_bonding_count / valid_traj_count, 2))

    plot(h_bonding_freq, ntraj)

def plot(data: List[int], ntraj: int) -> None:
    plt.plot(list(range(ntraj)), data)
    plt.title('H Bonding Analysis')
    plt.xlabel('Step Number')
    plt.ylabel('Ratio')
    plt.savefig('frequency_test.png')
    plt.show()

if __name__ == '__main__':
    run(ROOT_DIR, NAME)
