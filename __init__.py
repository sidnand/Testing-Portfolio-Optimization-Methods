#!/usr/bin/env python3

from src.app import App

from src.models.noGamma.ew import EqualWeight
from src.models.noGamma.JagannathanMa import JagannathanMa
from src.models.noGamma.kanZhouEw import KanZhouEw
from src.models.noGamma.minVar import MinVar
from src.models.noGamma.minVarShortSellCon import MinVarShortSellCon

from src.models.gamma.meanVar import MeanVar
from src.models.gamma.meanVarShortSellCon import MeanVarShortSellCon
from src.models.gamma.kanZhou import KanZhou
from src.models.gamma.bayesStein import BayesStein
from src.models.gamma.bayesSteinShortSellCon import BayesSteinShortSellCon
from src.models.gamma.macKinlayPastor import MacKinlayPastor

PATH = "data/new/processed/sp_sector.csv"
PATH_OLD = "data/old/SPSectors.txt"

# MODEL CONSTANTS

# Risk averse levels
GAMMAS = [1, 2, 3, 4, 5, 10]

OMEGAS = []

# Time horizons
TIME_HORIZON = [60, 120]

benchmark = EqualWeight("Equal Weight")
minVar = MinVar("Minimum Variance")
JagannathanMa = JagannathanMa("Jagannathan Ma")
minVarShortSellCon = MinVarShortSellCon("Minimum Variance with Short Sell Constrains")
kanZhouEw = KanZhouEw("Kan Zhou EW")

meanVar = MeanVar("Mean Variance (Markowitz)")
meanVarShortSellCon = MeanVarShortSellCon("Mean Variance with Short Sell Constrains")
kanZhou = KanZhou("Kan Zhou Three Fund")
bayesStein = BayesStein("Bayes Stein")
bayesSteinShortSellCon = BayesSteinShortSellCon("Bayes Stein with Short Sell Constrains")
macKinlayPastor = MacKinlayPastor("MacKinlay and Pastor")

models = [
    benchmark,
    minVar,
    JagannathanMa,
    minVarShortSellCon,
    kanZhouEw,
    meanVar,
    meanVarShortSellCon,
    kanZhou,
    bayesStein,
    bayesSteinShortSellCon,
    macKinlayPastor
]

def main() -> None:
    # app = App(PATH, GAMMAS, OMEGAS, TIME_HORIZON, models, 1)
    # app = App(PATH_OLD, GAMMAS, OMEGAS, TIME_HORIZON, models, 1, delim="\s+", date=True)
    # app = App(PATH, GAMMAS, OMEGAS, TIME_HORIZON, models, riskFactorPositions = [0])
    app = App(PATH_OLD, GAMMAS, OMEGAS, TIME_HORIZON, models,
              delim="\s+", date=True, riskFactorPositions=[0])

    sr = app.getSharpeRatios()
    sig = app.getStatisticalSignificanceWRTBenchmark(benchmark)

    print("Sharpe Ratios")

    for key, value in sr.items():
        print("{}: {}".format(key, value))

    print()
    print()

    print("Statistical Significances")

    for key, value in sig.items():
        print("{}: {}".format(key, value))

if __name__ == "__main__":
    main()