from __future__ import division, print_function, absolute_import
import numpy as np
from scipy import ndimage

__all__ = ["EqualGridInterpolator"]


class EqualGridInterpolator(object):
    """
    Interpolation on a equal spaced regular grid in arbitrary dimensions.
    Fock from https://github.com/JohannesBuchner/regulargrid
    """

    def __init__(self, points, values, order=1, padding='constant', fill_value=np.nan):
        '''
        points : tuple of ndarray, with shapes (m1, ), ..., (mn, )
            The points defining the equal regular grid in n dimensions.
        values : array_like, shape (m1, ..., mn, ...)
            The data on the regular grid in n dimensions.
        order : int
            The order of the spline interpolation, default is 1. 
            The order has to be in the range 0 to 5. 0 means nearest interpolation.
        padding : str
            Points outside the boundaries of the input are filled according
            to the given mode ('constant', 'nearest', 'reflect' or 'wrap').
        fill_value : number, optional
            If provided, the value to use for points outside of the interpolation domain.
        '''
        assert order in range(6)

        values = np.asfarray(values)
        assert len(points) == values.ndim

        points = [np.asarray(p) for p in points]
        for i, p in enumerate(points):
            assert len(p) > 1 & p.ndim == 1
            assert len(p) == values.shape[i]
            assert p[0] != p[1]
            assert np.allclose(np.diff(p), p[1] - p[0])

        self.order = order
        self.padding = padding
        self.fill_value = fill_value

        self.grid = tuple(points)
        self.values = values
        self.edges = tuple([p[0] for p in points])
        self.steps = tuple([p[1] - p[0] for p in points])
        self.coeffs = {0:self.values, 1:self.values}


    def __call__(self, xi, order=None):
        '''
        xi : ndarray of shape (..., ndim)
            The coordinates to sample the gridded data at.
        order : int
            The order of the spline interpolation.
        '''
        order = self.order if order is None else order
        assert order in range(6)
        assert len(xi) == self.values.ndim

        xi = [(x - xmin) / dx
              for x, xmin, dx in zip(xi, self.edges, self.steps)]
        input = self._coeffs(order)
        return ndimage.map_coordinates(input, xi, 
                               order=order, prefilter=False, 
                               mode=self.padding, cval=self.fill_value)


    def _coeffs(self, order):
        if order not in self.coeffs:
            # if more speedup is needed, add keywords `output=np.float32`?
            coeff = ndimage.spline_filter(self.values, order=order)
            self.coeffs[order] = coeff
        return self.coeffs[order]



if __name__ == "__main__":
    import numpy as np
    from scipy.interpolate import RegularGridInterpolator
    from matplotlib import pyplot as plt

    # Example 1
    f = lambda x, y: np.sin(x / 2) - np.sin(y)
    x, y = np.linspace(-2, 3, 5), np.linspace(-3, 2, 6)
    z = f(*np.meshgrid(x, y))

    xi, yi = np.meshgrid(np.linspace(-2, 3, 50), np.linspace(-3, 2, 60))
    zi1 = EqualGridInterpolator((x, y), z.T, order=1)((xi, yi))
    zi2 = RegularGridInterpolator((x, y), z.T)((xi, yi))
    assert np.allclose(zi1, zi2)
    zi1 = EqualGridInterpolator((x, y), z.T, order=0)((xi, yi))
    zi2 = RegularGridInterpolator((x, y), z.T, method='nearest')((xi, yi))
    assert np.allclose(zi1, zi2)


    f = lambda x, y: x * y
    mid = lambda x: (x[1:] + x[:-1]) / 2.
    x = np.linspace(0, 2, 10)
    y = np.linspace(0, 2, 15)
    x_, y_ = mid(x), mid(y)
    z = f(*np.meshgrid(x_, y_))

    # Example 2
    xi = np.linspace(0, 2, 40)
    yi = np.linspace(0, 2, 60)
    xi_, yi_ = mid(xi), mid(yi)

    zi1 = EqualGridInterpolator((x_, y_), z.T, order=3)(np.meshgrid(xi_, yi_))
    zi2 = EqualGridInterpolator((x_, y_), z.T)(np.meshgrid(xi_, yi_))
    zi3 = EqualGridInterpolator((x_, y_), z.T, padding='nearest')(np.meshgrid(xi_, yi_))

    plt.figure(figsize=(9, 9))
    plt.viridis()
    plt.subplot(221)
    plt.pcolormesh(x, y, z)
    plt.subplot(222)
    plt.pcolormesh(xi, yi, np.ma.array(zi1, mask=np.isnan(zi1)))
    plt.subplot(223)
    plt.pcolormesh(xi, yi, np.ma.array(zi2, mask=np.isnan(zi2)))
    plt.subplot(224)
    plt.pcolormesh(xi, yi, zi3)
    plt.show()
