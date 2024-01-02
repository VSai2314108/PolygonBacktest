from abc import ABC, abstractmethod
class Strategy(ABC):    
    @abstractmethod
    def algorithim(self, symbol, data):
        pass
    
    @abstractmethod
    def evaluate(self):
        pass
    