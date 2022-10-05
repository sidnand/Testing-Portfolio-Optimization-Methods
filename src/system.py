# CODE FOR RUNNING THE MODELS USING THE DATA

import math

import numpy as np

from models import *
from enum_policy import *

class System:
    
    """
    
        param riskFree : [m x 1] array of risk free assets
        param risky : [m x n] array of risky assets
        param M : estimation window length
    
    """
    def __init__(self, riskFree, risky, M):
        self.riskFree = riskFree
        self.risky = risky
        self.M = M

        self.ROWS = len(riskFree)
        self.COLS = 1 + np.shape(risky)[1]
        self.N = self.COLS - 1 # number of risky variables

    """
        Computes the sharpe ratios of all the portfolio policies

        returns : Object of floas denoting the sharpe ratio of each portfolio policy
    """
    def getSharpeRatios(self):
        w = {} # portfolio policy weights
        wBuyHold = {} # portfolio weights before rebalancing
        outSample = {} # out of sample returns

        for i in Policy:
            w[i.value] = np.empty((self.N, self.ROWS - self.M))
            wBuyHold[i.value] = np.empty((self.N, self.ROWS - self.M))
            outSample[i.value] = np.empty((1, self.ROWS - self.M))

        T = len(self.risky) # time period
        nSubsets = 1 if self.M == T else T - self.M # if M is the same as time period, then we only have 1 subset

        for shift in range(0, nSubsets):

            riskySubset = self.risky[shift:self.M + shift, :]
            riskFreeSubset = self.riskFree[shift:self.M + shift]
            subset = np.column_stack((riskFreeSubset, riskySubset))
            
            mu = np.array([np.mean(riskFreeSubset)])
            mu = np.append(mu, np.vstack(riskySubset.mean(axis = 0)))
            
            totalSigma = np.cov(subset.T)
            sigma = (self.M - 1) / (self.M - self.N - 1 - 2) * np.cov(riskySubset.T)
            
            sigmaMLE = (self.M - 1) / self.M * np.cov(riskySubset.T)
            invSigmaMLE = np.linalg.inv(sigmaMLE)

            AMLE = np.ones((1, self.COLS - 1)).dot(invSigmaMLE).dot(np.ones((self.COLS - 1, 1)))
            
            # 0: 1/N
            alphaTew = ew(self.COLS)
            w[Policy.EW][:, shift] = alphaTew[:, 0]
            
            # 5: minimum-variance
            alphaMV = minVar(invSigmaMLE, AMLE, self.COLS)
            w[Policy.MINIMUM_VAR][:, shift] = alphaMV[:, 0]

            # 10: minimum-variance shortsell constraints
            minVarCon = minVarConstrained(sigmaMLE)
            w[Policy.MINIMUM_VAR_CONSTRAINED][:, shift] = minVarCon[:, 0]

            minVarGCon = jagannathanMa(sigmaMLE)
            w[Policy.MINIMUM_VAR_GENERALIZED_CONSTRAINED][:, shift] = minVarGCon[:, 0]

            # buy and hold
            if shift == 0:
                wBuyHold[Policy.EW][:, shift]= alphaTew[:, 0]
                wBuyHold[Policy.MINIMUM_VAR][:, shift]= alphaMV[:, 0]
                wBuyHold[Policy.MINIMUM_VAR_CONSTRAINED][:, shift] = minVarCon[:, 0]
                wBuyHold[Policy.MINIMUM_VAR_GENERALIZED_CONSTRAINED][:, shift] = minVarGCon[:, 0]
            else:
                wBuyHold[Policy.EW][:, shift] = self.buyHold(w[Policy.EW][:, shift - 1], shift)
                wBuyHold[Policy.MINIMUM_VAR][:, shift] = self.buyHold(w[Policy.MINIMUM_VAR][:, shift - 1], shift)
                wBuyHold[Policy.MINIMUM_VAR_CONSTRAINED][:, shift] = self.buyHold(w[Policy.MINIMUM_VAR_CONSTRAINED][:, shift - 1], shift)
                wBuyHold[Policy.MINIMUM_VAR_GENERALIZED_CONSTRAINED][:, shift] = self.buyHold(w[Policy.MINIMUM_VAR_GENERALIZED_CONSTRAINED][:, shift - 1], shift)
                
            if (nSubsets > 1):
            # out of sample returns
                outSample[Policy.EW][:, shift] = self.outOfSampleReturns(alphaTew, shift)[:, 0]
                outSample[Policy.MINIMUM_VAR][:, shift] = self.outOfSampleReturns(alphaMV, shift)[:, 0]
                outSample[Policy.MINIMUM_VAR_CONSTRAINED][:, shift] = self.outOfSampleReturns(minVarCon, shift)[:, 0]
                outSample[Policy.MINIMUM_VAR_GENERALIZED_CONSTRAINED][:, shift] = self.outOfSampleReturns(minVarGCon, shift)[:, 0]

        sharpeRatios = {}
        for i in Policy:
            sharpeRatios[i.value] = round(self.sharpeRato(outSample[i.value]), 4)

        return sharpeRatios

    """

        Computes a new portfolio weight after a shift

        param w : [n, row - M] array, holds portfolio weights of a specific policy
        param j : integer value, represents current shift position

    """
    def buyHold(self, w, j):

        a = (1 - sum(w)) * (1 + self.riskFree[self.M + j])
        b = (1 + (self.risky[self.M + j, :].T + self.riskFree[self.M + j]))[np.newaxis].T
        trp = a + w[np.newaxis].dot(b)
        
        return ((w * (1 + (self.risky[self.M + j, :]).T + self.riskFree[self.M + j])) / trp)

    """

        Computes the out of sample returns

        param w : [n, row - M] array, holds portfolio weights of a specific policy
        param j : integer value, represents current shift position

    """
    def outOfSampleReturns(self, w, j):
        return w.T.dot(self.risky[self.M + j, :][np.newaxis].T)

    """

        Computes the Sharpe ratio

        param x : [1, rows - M] array, holds the out of sample return values

        returns : real number

    """
    def sharpeRato(self, x):
        mean = np.mean(x.T)
        std = np.std(x.T, ddof = 1)
        
        if (abs(mean) > pow(10, -16)):
            sr = mean / std;
        else:
            sr = None
                
        return sr