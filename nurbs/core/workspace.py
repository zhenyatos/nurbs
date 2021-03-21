import pygame as pg
import typing as t
import nurbs.const as const
import nurbs.core.nurbspline as nurbspline
import math


class Workspace:
	def __init__(self, size_x: int, size_y: int, pos_grid: t.Tuple[int, int]):
		if not isinstance(size_x, int) or not isinstance(size_y, int):
			raise TypeError('invalid type')
		if not isinstance(pos_grid, tuple) or len(pos_grid) != 2:
			raise TypeError('invalid type')
		if not 0 < size_x <= const.WINDOW_SIZE[0] or not 0 < size_y <= const.WINDOW_SIZE[1]:
			raise ValueError('invalid size')

		self.__size = (size_x, size_y)
		self.__pos_grid = pos_grid
		self.__surf_grid = pg.Surface((size_x, size_y)).convert()
		self.__surf_work = pg.Surface((size_x, size_y)).convert()
		self.__surf_grid.fill(const.COLOR_WORKSPACE)
		xticks = size_x // const.WORKSPACE_AXIS_TICK_SIZE
		yticks = size_y // const.WORKSPACE_AXIS_TICK_SIZE
		last_pixel_x = size_x - 1
		last_pixel_y = size_y - 1
		for xtick in range(xticks + 1):
			offset_x = min(xtick * const.WORKSPACE_AXIS_TICK_SIZE, last_pixel_x)
			pg.draw.aaline(self.__surf_grid, const.COLOR_GRID, (offset_x, 0), (offset_x, last_pixel_y))
		for ytick in range(yticks + 1):
			offset_y = min(ytick * const.WORKSPACE_AXIS_TICK_SIZE, last_pixel_y)
			pg.draw.aaline(self.__surf_grid, const.COLOR_GRID, (0, offset_y), (last_pixel_x, offset_y))
		self.__font = pg.font.SysFont(const.WORKSPACE_FONT['style'], const.WORKSPACE_FONT['size'])
		self.__nurbspline = nurbspline.NURBSpline(const.BSPLINE_DEGREE_MIN)
		self.__curve = None

		# updatable info
		self.__pos_mouse = [-1, -1]
		self.__points = []
		self.__inv_points = []
		self.__point_curr = None
		self.__point_drag = False
		self.__point_add = False
		self.__point_rem = False

	def __is_mouse_on_grid(self) -> bool:
		on_grid = 0 <= self.__pos_mouse[0] < self.__size[0] and 0 <= self.__pos_mouse[1] < self.__size[1]
		if not on_grid:
			self.__point_add = False
			self.__point_rem = False
		return on_grid

	def __set_point_curr(self) -> None:
		self.__point_curr = None
		for point_center in reversed(self.__points):
			if math.sqrt(
				(self.__pos_mouse[0] - point_center[0]) ** 2 + 
				(self.__pos_mouse[1] - point_center[1]) ** 2) <= const.WORKSPACE_POINTS_RAD:
				self.__point_curr = point_center
				return
		self.__point_rem = False

	def __recalc_spline(self) -> None:
		self.__curve = self.__nurbspline.recalc(self.__points)
		if self.__curve:
			for i in range(len(self.__curve)):
				self.__curve[i][1] = self.__size[1] - self.__curve[i][1]

	def draw(self, surf: pg.Surface) -> None:
		self.__surf_work.blit(self.__surf_grid, (0, 0))
		if self.__curve:
			pg.draw.aalines(self.__surf_work, const.COLOR_GREEN, closed=False, points=self.__curve)
			pg.draw.aalines(self.__surf_work, const.COLOR_BLACK, closed=False, points=self.__inv_points)
		for i in range(len(self.__points)):
			if self.__point_curr != self.__points[i]:
				color = const.COLOR_BLUE
			else:
				color = const.COLOR_RED if self.__point_drag else const.COLOR_GREEN
			pg.draw.circle(
				self.__surf_work, color,
				(self.__points[i][0], (self.__size[1] - self.__points[i][1])), 
				const.WORKSPACE_POINTS_RAD)

		self.__surf_work.blit(self.__font.render(
			'points: %2d/%2d' % (len(self.__points), const.WORKSPACE_POINTS_MAX), 
			True, const.WORKSPACE_FONT['color']), 
			(const.WORKSPACE_FONT['indent'], 0))
		self.__surf_work.blit(self.__font.render(
			'degree: %2d/%2d' % (self.__nurbspline.degree, const.BSPLINE_DEGREE_MAX), 
			True, const.WORKSPACE_FONT['color']), 
			(const.WORKSPACE_FONT['indent'], const.WORKSPACE_FONT['size'] + const.WORKSPACE_FONT['indent']))
		if self.__is_mouse_on_grid():
			self.__surf_work.blit(self.__font.render(
				'x:%4d y:%4d' % (self.__pos_mouse[0],  self.__pos_mouse[1]), 
				True, const.WORKSPACE_FONT['color']), 
				(const.WORKSPACE_FONT['indent'], (const.WORKSPACE_FONT['size'] + const.WORKSPACE_FONT['indent']) * 2))

		surf.blit(self.__surf_work, self.__pos_grid)

	def on_mouse_hover(self, pos_mouse: t.Tuple[int, int]) -> None:
		self.__pos_mouse[0] = pos_mouse[0] - self.__pos_grid[0]
		self.__pos_mouse[1] = self.__size[1] - (pos_mouse[1] - self.__pos_grid[1])
		if not self.__is_mouse_on_grid():
			self.__point_drag = False
			return
		if self.__point_drag:
			idx = self.__inv_points.index((self.__point_curr[0], self.__size[1] - self.__point_curr[1]))
			self.__point_curr[0] = self.__pos_mouse[0]
			self.__point_curr[1] = self.__pos_mouse[1]
			self.__inv_points[idx] = (self.__point_curr[0], self.__size[1] - self.__point_curr[1])
			#self.__points.sort(key=lambda point: point[0])
			self.__recalc_spline()
		else:
			self.__set_point_curr()

	def on_mouse_button_down(self, button: int) -> None:
		if not self.__is_mouse_on_grid():
			return
		if button == 1:
			if self.__point_curr:
				self.__point_drag = True
			else:
				self.__point_add = True
		if button == 3:
			if self.__point_curr:
				self.__point_rem = True
			else:
				self.__point_rem = False

	def on_mouse_button_up(self, button: int) -> None:
		if button == 4:
			self.__nurbspline.degree = min(const.BSPLINE_DEGREE_MAX, self.__nurbspline.degree + 1)
			return
		if button == 5:
			self.__nurbspline.degree = max(const.BSPLINE_DEGREE_MIN, self.__nurbspline.degree - 1)
			return
		if not self.__is_mouse_on_grid():
			self.__point_drag = False
			return
		if button == 1:
			if not self.__point_drag and self.__point_add:
				if len(self.__points) < const.WORKSPACE_POINTS_MAX:
					mouse_pt = self.__pos_mouse.copy()
					self.__points.append(mouse_pt)
					self.__inv_points.append((mouse_pt[0], self.__size[1] - mouse_pt[1]))
					#self.__points.sort(key=lambda point: point[0])
					self.__recalc_spline()
				self.__point_add = False
			self.__point_drag = False
		elif button == 3:
			if self.__point_curr and self.__point_rem:
				self.__points.remove(self.__point_curr)
				self.__inv_points.remove((self.__point_curr[0], self.__size[1] - self.__point_curr[1]))
				self.__recalc_spline()
			self.__point_rem = False
			self.__point_drag = False
