import typing as t
import numpy as np
from nurbs.const import N_DISCR_CURVE


class NURBSpline:
    def __init__(self, degree: int):
        self.__degree = degree
        self.__knots = np.asarray([])
        self.__basis = np.asarray([])

    @property
    def degree(self):
        return self.__degree

    @degree.setter
    def degree(self, degree: int):
        self.__degree = degree

    def recalc_knots(self, n_points):
        """
        Recalculating knots vector, using clamped at start + clamped at end strategy.

        :param n_points: number of control points
        :return: knots vector.
        """
        self.__knots = np.linspace(0, 1, n_points + self.degree + 1)
        self.__knots[0 : self.degree + 1] = 0
        self.__knots[-self.degree - 1 : -1] = 1

    def f(self, i, n, t_vec):
        """
        Auxiliary function f, rises linearly from 0 to 1 for t ∈ [knot_i, knot_{i+n}], that is
        the interval where basis_{i, n-1} is non zero
        """
        # denum can be zero if adjacent knots are equal, which is allowed, in this case f ≡ 0
        denum = self.__knots[i + n] - self.__knots[i]
        if denum == 0.0:
            return np.zeros(len(t_vec))
        return (t_vec - self.__knots[i]) / denum

    def g(self, i, n, t_vec):
        """
        Auxiliary function g, falls linearly from 1 to 0 for t ∈ [knot_{i+1}, knot_{i+n+1}], that is
        the interval where basis_{i+1, n-1} is non zero
        """
        denum = self.__knots[i + n + 1] - self.__knots[i + 1]
        # denum can be zero if adjacent knots are equal, which is allowed in this case g ≡ 0
        if denum == 0.0:
            return np.zeros(len(t_vec))
        return (self.__knots[i + n + 1] - t_vec) / denum

    def calc_basis_at_t(self, t_vec, n_points):
        """
        Calculate values of basis_{i, degree} where i = 0, ..., num_ctrl_points.

        :param t: curve parameter value
        :param n_points: number of control points
        :return: None.
        """
        self.__basis = np.zeros((len(t_vec), n_points + self.degree + 1, 2))

        for i in range(0, len(self.__knots) - 1):
            self.__basis[:, i, 0] = (self.__knots[i] <= t_vec) & (t_vec <= self.__knots[i + 1])

        for n in range(1, self.degree + 1):
            for i in range(0, len(self.__knots) - 1 - n):
                f = self.f(i, n, t_vec)
                g = self.g(i, n, t_vec)
                self.__basis[:, i, 1] = f * self.__basis[:, i, 0] + g * self.__basis[:, i + 1, 0]
            self.__basis[:, :, 0] = self.__basis[:, :, 1]

    def get_basis(self, k):
        return self.__basis[:, k, 1]

    def recalc(self, ctrl_points: t.List) -> t.Union[t.List, None]:
        """
        Recalculate NURBS.

        :param ctrl_points: control points
        :return: points of NURBS.
        """
        num_ctrl_pts = len(ctrl_points)
        if num_ctrl_pts < self.degree + 1:
            return None
        # points are sorted by x btw, don't worry
        self.recalc_knots(num_ctrl_pts)

        t_vec = np.linspace(self.__knots[0], self.__knots[-1], N_DISCR_CURVE)
        self.calc_basis_at_t(t_vec, num_ctrl_pts)
        pts = np.zeros((len(t_vec), 2))
        sum_basis = np.zeros(len(t_vec))
        for i in range(0, num_ctrl_pts):
            basis = self.get_basis(i)
            sum_basis += basis
            pts[:, 0:2] += np.multiply.outer(np.transpose(basis[:]), ctrl_points[i])
        pts[:, 0:2] = pts[:, 0:2] / np.array([sum_basis, ] * 2).transpose()
        return pts[:, 0:2]
