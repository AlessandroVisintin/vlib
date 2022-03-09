import numpy as np
import opensimplex as sx


class GradientNoise:
    
    
    def __init__(self, size, scale=(1,1), seed=-1):
        self.sz = size
        self.I = np.array(list(range(self.sz[0])), dtype='uint64')
        self.J = np.array(list(range(self.sz[1])), dtype='uint64')
        self.change_scale(scale)
        self.change_seed(seed)


    def change_scale(self, scale):
        self.sc = scale
        self.Is = self.I / self.sc[0]
        self.Js = self.J / self.sc[1]


    def change_seed(self, seed):
        if seed < 0:
            sx.seed(np.random.randint(2**20))
        else:
            sx.seed(np.random.randint(seed))


    def g2D(self, norm=(-1,1)):
        out = sx.noise2array(self.Is, self.Js)
        return norm[0] + (norm[1] - norm[0]) * ((out+1) / 2)
    