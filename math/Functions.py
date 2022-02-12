import numpy as np


class Functions:
    
    @staticmethod
    def sigmoid(x, a=0, b=1, c=1, k=1, q=1, v=1):
        return a + ((k-a) / (c + q*np.exp(-b*x)))**(1/v)


if __name__ == '__main__':
    
    import matplotlib.pyplot as plt
    
    X = np.arange(-10,10)
    Y = Functions.sigmoid(X)
    
    plt.plot(X,Y)
    plt.show()