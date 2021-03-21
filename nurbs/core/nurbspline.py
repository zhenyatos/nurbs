import typing as t
import numpy as np
from math import fabs
from nurbs.const import FLOAT_PRECISION


class NURBSpline:
    def __init__(self, degree: int):
        self.__degree = degree
        self.__knots = []
        self.__basis = np.asarray([])

    @property
    def degree(self):
        return self.__degree

    @degree.setter
    def degree(self, degree: int):
        self.__degree = degree

    def recalc_knots(self, points: t.List):
        n_halves = len(points) - self.degree - 1
        self.__knots = \
            [0] * (self.degree + 1) + [0.5] * n_halves + [1] * (self.degree + 1)
        self.__knots = [i for i in np.linspace(0, 1, len(points) + self.degree + 1)]

    def f(self, i, n, t):
        assert(i >= 1)
        denum = self.__knots[i + n - 1] - self.__knots[i - 1]
        return (t - self.__knots[i - 1]) / denum\
            if fabs(denum) > FLOAT_PRECISION else 0

    def g(self, i, n, t):
        assert (i >= 1)
        denum = self.__knots[i + n - 1] - self.__knots[i - 1]
        return (self.__knots[i + n - 1] - t) / denum\
            if fabs(denum) > FLOAT_PRECISION else 0

    def calc_basis_at_t(self, t, num_ctrl_pts):
        # -------n---------> degree
        # |XXXXXX
        # |XXXXXX
        # |XXXXX
        # |XXXX
        # |XXX
        # |XX
        # |X
        # i + n
        # V
        # i
        self.__basis = np.zeros((num_ctrl_pts + self.degree + 1, self.degree + 1))

        for i in range(1, num_ctrl_pts + self.degree):
            # max(0, i - 1)
            # min(i + self.degree, len(self.__knots) - 1)
            self.__basis[i, 0] = self.__knots[i - 1] <= t and \
                          t <= self.__knots[i]
            # or fabs(self.__knots[i + 1] - self.__knots[i]) < FLOAT_PRECISION) \

        self.__basis[0, 0] = self.__knots[0] <= t <= self.__knots[1]

        for n in range(1, self.degree + 1):
            for i in range(self.degree - n + num_ctrl_pts, 0, -1):
                f = self.f(i, n, t)
                g = self.g(i + 1, n, t)
                assert(self.__basis[i][n - 1] >= -FLOAT_PRECISION)
                assert(self.__basis[i + 1][n - 1] >= -FLOAT_PRECISION)
                self.__basis[i, n] = \
                    f * self.__basis[i][n - 1] + \
                    g * self.__basis[i + 1][n - 1]

    def get_basis(self, k) -> float:
        return self.__basis[k][self.degree]

    def recalc(self, ctrl_points: t.List) -> t.Union[t.List, None]:
        num_ctrl_pts = len(ctrl_points)
        if num_ctrl_pts < self.degree + 1:
            return None
        # points are sorted by x btw, don't worry
        self.recalc_knots(ctrl_points)

        points = []
        for t in np.linspace(0, 1, 100):
            pt = np.asarray([0, 0], dtype=float)
            self.calc_basis_at_t(t, num_ctrl_pts)
            for i in range(0, num_ctrl_pts):
                basis = self.get_basis(i)
                print(f"basis:{basis}")
                pt += np.asarray(ctrl_points[i]) * basis
            points.append(pt)
        return points
