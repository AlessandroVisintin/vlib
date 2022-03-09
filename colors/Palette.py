import numpy as np
from vlib.colors.functions import hex2rgb, rgb2hex, rgb2lab, contrast


class Palette:
    
    
    def __init__(self, name, **kwargs):
        self.name = name
        if 'hexs' in kwargs:
            self.hexs = kwargs['hexs']
            self.rgbs = [hex2rgb(h) for h in kwargs['hexs']]
        elif 'rgbs' in kwargs:
            self.hexs = [rgb2hex(r) for r in kwargs['rgbs']]
            self.rgbs = kwargs['rgbs'] 
        else:
            raise RuntimeError('Missing color palette.')
        self.labs = rgb2lab(self.rgbs)


    def list_by_luminosity(self):
        return
#        nodes = list(self.pal.nodes())
#        sp = single_source_dijkstra(self.pal, nodes[0], weight='lumin')
#        return sp

    
    def get_by_contrast(self, num):
        out = []
        for i,ri in enumerate(self.rgbs):
            c = [contrast(ri, rj) for j, rj in enumerate(self.rgbs) if i != j]
            c = list(sorted(c, reverse=True))[:num-1]
            out.append((i, np.sqrt(np.sum(np.square(c)))))
        out = list(sorted(out, key=lambda t:t[1], reverse=True))
        idx, _ = list(zip(*out))
        return idx[:num]


class PaletteManager:
    

    def __init__(self, pal_file):
        self.pals = []
        with open(pal_file, 'r') as f:
            for line in f:
                line = line.strip().split(' ')
                nm, hs = (line[0], [h for h in line[1].split(',')])
                self.pals.append(Palette(nm, hexs=hs))
    
    
    def get_by_contrast(self, num):
        for pal in self.pals:
            idxs = pal.get_by_contrast(num)
            yield (
                    pal.name, 
                    [pal.hexs[i] for i in idxs],
                    [pal.rgbs[i] for i in idxs],
                    [pal.labs[i] for i in idxs]
                )
            