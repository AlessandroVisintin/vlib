import numpy as np
from PIL import Image, ImageDraw
from vlib.random.GradientNoise import GradientNoise


class VectorField:
    
    
    def __init__(self, size, step=1, init=None, **kwargs):
        self.sz = size
        self.st = step
        self._sz = (
            int(np.ceil(self.sz[0] / self.st)),
            int(np.ceil(self.sz[1] / self.st))
        )
        
        if init is None:
            self.vf = np.zeros(self._sz)
        elif init == 'constant':
            self.vf = np.full(self._sz, kwargs['value'])
        elif init == 'gradient':
            seed = -1
            if 'seed' in kwargs:
                seed = kwargs['seed']
            gn = GradientNoise(self._sz, scale=(self.st,self.st), seed=seed)
            self.vf = gn.g2D(norm=(0,2*np.pi)) 
        else:
            raise RuntimeError('Invalid init keyword.')
    
    
    def _scale2norm(self, x, y):
        return (int((x+0.5) * self.st), int((y+0.5) * self.st))
    
    
    def _norm2scale(self, x, y):
        return (int(x / self.st), int(y / self.st))
    
    
    def show(self, border=False, path=None):
        im = Image.new('RGB', self.sz, (255,255,255))
        imd = ImageDraw.Draw(im)
        for i in range(self._sz[0]):
            for j in range(self._sz[1]):
                a, l = self.vf[i,j], self.st / 4
                p1 = self._scale2norm(j, i)
                p2 = (int(p1[0] +  l*np.cos(a)), int(p1[1] + l*np.sin(a)))
                imd.line([p1,p2], fill=(0,0,0), width=1)
        if border:
            h,w = self.sz
            bds = [(0,0), (0,h-1), (w-1,h-1), (w-1,0), (0,0)]
            imd.line(bds, fill=(0,0,0), width=1)
        if path is not None:
            path = [(j,i) for i,j in path]
            imd.line(path, fill=(0,0,0), width=2)
        im.show()


    def get_path(self, start, max_iter=float('inf')):
        i,j = start
        lst = []
        while (0 <= i < self.sz[0])  and (0 <= j < self.sz[1]):
            lst.append((i,j))
            if len(lst) >= max_iter:
                break
            i_s, j_s = self._norm2scale(i,j)
            a = self.vf[i_s,j_s]
            i, j = (i + self.st * np.sin(a), j + self.st * np.cos(a))
        return lst
            