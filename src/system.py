# CODE FOR RUNNING THE MODELS USING THE DATA

import numpy as np

from .utils.statistics import *

class System:
    
    def __init__(self, data, timeHorizon, models, gamma):
        (self.m, self.n) = data.shape

        self.riskFreeReturns = data[:, 0] # risk-free asset column
        self.riskyReturns = data[:, 1:self.n] # risky asset column, includes risk factor
        self.timeHorizon = timeHorizon # estimation window length
        self.models = models
        self.gamma = gamma

        self.nRisky = self.n - 1 # number of risky variables
        self.T = len(self.riskyReturns) # time period
        self.upperM = self.timeHorizon[-1] # upper bound of time horizon

        self.weights = {} # portfolio policy weights
        self.weightsBuyHold = {} # portfolio weights before rebalancing
        self.outSample = {} # out of sample returns
        self.initDicts()

        self.run()

    def initDicts(self):
        for model in self.models:
            self.weights[model.name] = np.empty((self.nRisky, self.m - self.timeHorizon[-1]))
            self.weightsBuyHold[model.name] = np.empty((self.nRisky, self.m - self.timeHorizon[-1]))
            self.outSample[model.name] = np.empty((1, self.m - self.timeHorizon[-1]))

    def run(self):
        for k in self.timeHorizon:
            m = k # time horizon
            shift = self.upperM - m # shift in time horizon
            m = m + shift # update time horizon
            
            nSubsets = 1 if m == self.T else self.T - m # if m is the same as time period, then we only have 1 subset

            for j in range(0, nSubsets):

                riskySubset = self.riskyReturns[j+shift:m+j-1, :]
                riskFreeSubset = self.riskFreeReturns[j+shift:m+j-1]
                subset = np.column_stack((riskFreeSubset, riskySubset))

                nRisky = len(riskySubset)
                
                mu_horz = np.array([np.mean(riskFreeSubset)])
                mu = np.append(mu_horz, np.vstack(riskySubset.mean(axis = 0)))
                
                totalSigma = np.cov(subset.T)
                sigma = (m - 1) / (m - self.nRisky - 2) * np.cov(riskySubset.T)
                
                sigmaMLE = (m - 1) / m * np.cov(riskySubset.T)
                invSigmaMLE = np.linalg.inv(sigmaMLE)

                amle = np.ones((1, self.nRisky)) @ invSigmaMLE @ np.ones((self.nRisky, 1))

                params = {
                    "n": self.n,
                    "sigma": sigma,
                    "sigmaMLE": sigmaMLE,
                    "invSigmaMLE": invSigmaMLE,
                    "amle": amle,
                    "gamma": self.gamma,
                    "nRisky": self.nRisky,
                    "m": m,
                    "mu": mu
                }

                for model in self.models:
                    name = model.name
                    alpha = model.alpha(params)

                    self.weights[name][:, j] = alpha[:, 0]

                    if j == 0: self.weightsBuyHold[name][:, j] = alpha[:, 0]
                    else: self.weightsBuyHold[name][:, j] = self.buyHold(self.weights[name][:, j - 1], j, m)

                    if (nSubsets > 1): self.outSample[name][:, j] = self.outOfSampleReturns(alpha, j, m)[:, 0]

    def getSharpeRatios(self):
        sr = {}

        for model in self.models:
            sr[model.name] = sharpeRato(self.outSample[model.name])

        return sr

    def buyHold(self, weights, j, m):
        a = (1 - sum(weights)) * (1 + self.riskFreeReturns[m + j])
        b = (1 + (self.riskyReturns[m + j, :].T + self.riskFreeReturns[m + j]))[np.newaxis].T
        trp = a + weights[np.newaxis].dot(b)
        
        return ((weights * (1 + (self.riskyReturns[m + j, :]).T + self.riskFreeReturns[m + j])) / trp)

    def outOfSampleReturns(self, weights, j, m):
        return weights.T.dot(self.riskyReturns[m + j, :][np.newaxis].T)