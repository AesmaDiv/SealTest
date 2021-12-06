"""
    Модуль содержит функции для расчёта интерполируемого
    кубического сплайна
"""
import math
import numpy as np
from scipy.interpolate import make_interp_spline, splrep, splev
import matplotlib.pyplot as plt


def binomial(i, n):
    """Binomial coefficient"""
    return math.factorial(n) / float(math.factorial(i) * math.factorial(n - i))


def bernstein(t, i, n):
    """Bernstein polynom"""
    return binomial(i, n) * (t ** i) * ((1 - t) ** (n - i))


def bezier(t, points):
    """Calculate coordinate of a point in the bezier curve"""
    n = len(points) - 1
    x = y = 0
    for i, pos in enumerate(points):
        bern = bernstein(t, i, n)
        x += pos[0] * bern
        y += pos[1] * bern
    return x, y


def bezierCurveRange(n, points):
    """Range of points in a curve bezier"""
    for i in range(n):
        t = i / float(n - 1)
        yield bezier(t, points)


def getCurvePoints(x, y, is_bezier=False):
    """ получение точек кривой """
    tck = splrep(x, y)
    x2 = np.linspace(0, max(x), 200)
    y2 = splev(x2, tck)
    if is_bezier:
        knots = np.array([x[1]])
        weights = np.concatenate(([1], np.ones(len(x) - 2) * .01, [1]))
        tck = splrep(x, y, t=knots, w=weights)
        x3 = np.linspace(0, max(x), 200)
        y3 = splev(x2, tck)
        return x3, y3
    return x2, y2


def plotSplinePoints(points_x, points_y):
    """ построение графика по точкам """
    tck = splrep(points_x, points_y)
    x2 = np.linspace(0, max(points_x), 200)
    y2 = splev(x2, tck)
    knots = np.array([points_x[1]])
    weights = np.concatenate(([1], np.ones(len(points_x)-2)*.01, [1]))
    tck = splrep(points_x, points_y, t=knots, w=weights)
    x3 = np.linspace(0, max(points_x), 200)
    y3 = splev(x3, tck)
    plt.plot(points_x, points_y, 'go', x2, y2, 'b', x3, y3, 'r')
    plt.show()


def getBSplinePoints(points_x, points_y):
    """ получение сплайна из точек """
    np_x = np.array(points_x)
    np_y = np.array(points_y)
    new_x = np.linspace(np_x.min(), np_x.max(), 100)
    spline = make_interp_spline(np_x, np_y, k=2)
    new_y = spline(new_x)
    return new_x.tolist(), new_y.tolist()
