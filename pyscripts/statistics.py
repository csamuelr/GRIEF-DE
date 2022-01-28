from numpy import std
from numpy import mean
from numpy import var
from numpy import quantile

class Statistics:
    
    def __init__(self, obj):
        self.obj = obj
        self.mean = None
        self.standard_deviation = None
        self.variance = None
        self.quantile = None

        self.__mean()
        self.__variance()
        self.__standard_deviation()
        self.__quantile()


    def __mean(self):
        self.mean = mean(self.obj)


    def __standard_deviation(self):                
        self.standard_deviation = std(self.obj)


    def __variance(self):
       self.variance = var(self.obj)


    def __quantile(self):
        self.quantile = []
        for q in  [0.01, 0.25, 0.5, 0.75, 0.1]:    
            self.quantile.append(quantile(self.obj, q))
