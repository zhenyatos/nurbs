import typing as t
import numpy as np
from math import fabs


class NURBSpline:
    def __init__(self, degree: int):
        self.__degree = degree
        self.__knots = []

    @property
    def degree(self):
        return self.__degree

    @degree.setter
    def degree(self, degree: int):
        self.__degree = degree

    def recalc_knots(self, points: t.List):
        n_halves = len(points) - self.degree - 1
        self.__knots = \
            [0] * (self.degree + 1) + [0.5] * n_halves + [1] * (self.degree + 1 + 1)

    def f(self, i, n, t):
        denum = self.__knots[i + n] - self.__knots[i]
        return (t - self.__knots[i]) / denum if fabs(denum) > 1e-6 else 0

    def g(self, i, n, t):
        return 1 - self.f(i, n, t)

    def get_basis(self, k, t, num_ctrl_pts) -> float:
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
        basis = np.zeros((num_ctrl_pts + self.degree + 1, self.degree + 1))

        for i in range(0, num_ctrl_pts + self.degree):
            # max(0, i - 1)
            # min(i + self.degree, len(self.__knots) - 1)
            basis[i, 0] = 1 \
                if self.__knots[i] <= t and \
                   (t <= self.__knots[i + 1] or
                    fabs(self.__knots[i + 1] - self.__knots[i]) < 1e-6) \
                else 0

        basis[-1, 0] = 1

        for n in range(1, self.degree + 1):
            for i in range(self.degree - n + num_ctrl_pts, 0, -1):
                f = self.f(i, n, t)
                g = self.g(i + 1, n, t)
                assert(f * basis[i][n - 1] >= 0)
                assert(g * basis[i + 1][n - 1] >= 0)
                basis[i, n] = \
                    f * basis[i][n - 1] + \
                    g * basis[i + 1][n - 1]

        return basis[k][self.degree]

    def recalc(self, ctrl_points: t.List) -> t.Union[t.List, None]:
        num_ctrl_pts = len(ctrl_points)
        if num_ctrl_pts < self.degree + 1:
            return None
        # points are sorted by x btw, don't worry
        self.recalc_knots(ctrl_points)

        points = []
        for t in np.linspace(0, 1, 50):
            pt = np.asarray([0, 0], dtype=float)
            for i in range(0, num_ctrl_pts):
                basis = self.get_basis(i, t, num_ctrl_pts)
                print(f"basis:{basis}")
                pt += np.asarray(ctrl_points[i]) * basis
            points.append(pt)
        return points if len(points) >= 2 else None
