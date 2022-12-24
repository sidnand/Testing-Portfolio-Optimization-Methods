#!/usr/bin/env python3

import pandas as pd

from src.system import *

PATH_OLD = "data/old/SPSectors.txt"
PATH = "data/new/processed/sp_sector.csv"

# MODEL CONSTANTS

# Risk averse levels
GAMMA = [1, 2, 3, 4, 5, 10]

# Time horizon
TIME_HORIZON = [60, 120]

SPSectorsPandas = pd.read_table(PATH, sep = ",")
SPSectorsPandasOld = pd.read_table(PATH_OLD, sep = "\s+")

SPSectors = SPSectorsPandas.to_numpy()
SPSectorsOld = SPSectorsPandasOld.to_numpy()[:, 1:]

COLS = SPSectors.shape[1]
COLS_OLD = SPSectorsOld.shape[1]

def main() -> None:
    SYSTEM = System(SPSectors, TIME_HORIZON)
    # SYSTEM = System(SPSectorsOld, TIME_HORIZON)

    sr = SYSTEM.getSharpeRatios(GAMMA)

    for key, value in sr.items():
        print('Policy: ', key.value)

        for k, v in value.items():
            print("{} : {}".format(k, round(v, 4)))
        print()


if __name__ == "__main__":
    main()