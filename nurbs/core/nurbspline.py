import typing as t
import numpy as np


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
			[0] * (self.degree + 1) + [0.5] * n_halves + [1] * (self.degree + 1)

	def f(self, i, n, t):
		return (t - self.__knots[i]) / (self.__knots[i + n] - self.__knots[i])

	def g(self, i, n, t):
		return 1 - self.f(i, n, t)

	def get_basis(self, i, t, num_ctrl_pts) -> float:
		basis = [[0] * (self.degree + 1)] * (num_ctrl_pts + self.degree + 1)

		for k in range(0, i + num_ctrl_pts):
			basis[k][0] = 1 if\
				(0 <= k < self.degree + 1 and 0 <= t < self.degree + 1) or \
				(self.degree + 1 <= k < num_ctrl_pts and
				self.degree + 1 <= t < num_ctrl_pts) or\
				(num_ctrl_pts <= k < num_ctrl_pts + self.degree and
				num_ctrl_pts <= t < num_ctrl_pts + self.degree) else 0

		for k in range(1, self.degree + 1):
			for j in range(k + num_ctrl_pts + 1, -1, 1):
				basis[j][k] =\
					self.f(j, k, t) * basis[j][k - 1] +\
					self.g(j, k, t) * basis[j + 1][k - 1]

		return basis[i][self.degree]

	def recalc(self, ctrl_points: t.List) -> t.Union[t.List, None]:
		# points are sorted by x btw, don't worry
		self.recalc_knots(ctrl_points)

		points = []
		len_ctrl_pts = len(ctrl_points)
		for t in np.linspace(0, 10, 100):
			pt = np.asarray([0, 0])
			for i in range(0, len_ctrl_pts):
				pt += np.asarray(ctrl_points[i]) *\
					self.get_basis(i, t, len_ctrl_pts)
			points.append(pt)
		return points if len(points) >= 2 else None
