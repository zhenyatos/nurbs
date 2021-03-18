import typing as t

class NURBSpline:
	def __init__(self, degree: int):
		self.__degree = degree

	@property
	def degree(self):
		return self.__degree

	@degree.setter
	def degree(self, degree: int):
		self.__degree = degree
	
	def recalc(self, points: t.List) -> t.Union[t.List, None]:
		# points are sorted by x btw, don't worry
		return [point.copy() for point in points] if len(points) >= 2 else None
