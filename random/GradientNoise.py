import numpy as np
from opensimplex import seed, noise2array
from vlib.math.Functions import sigmoid


class GradientNoise:
    
    
    @staticmethod
    def pts(x, y, max_seed=2**20, scale=1):
        seed(np.random.randint(max_seed))
        return noise2array(np.array(x), np.array(y))**(scale)
    
    
    @staticmethod
    def grid(h, w, scale=1):
        rows, cols = list(range(h)), list(range(w))
        return GradientNoise.pts(rows, cols, scale=scale)


if __name__ == "__main__":
    
    from PIL import Image
    
    grid = GradientNoise.grid(1000, 1000, 1/4) * 255
    im = Image.fromarray(grid)
    im.show()
    
    