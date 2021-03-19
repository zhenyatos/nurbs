import pygame.locals as pl

WINDOW_CAPTION = "nurbs"
WINDOW_SIZE = (1280, 720)
WINDOW_FLAGS = pl.FULLSCREEN

COLOR_CANVAS = (200, 200, 200)
COLOR_WORKSPACE = (220, 220, 220)
COLOR_GRID = (180, 180, 180)
COLOR_RED = (220, 0, 0)
COLOR_BLUE = (0, 0, 220)
COLOR_GREEN = (0, 220, 0)
COLOR_GRAY = (160, 160, 160)
COLOR_BLACK = (0, 0, 0)

WORKSPACE_SIZE_X = 800
WORKSPACE_SIZE_Y = 400
WORKSPACE_AXIS_TICK_SIZE = 50
WORKSPACE_POINTS_MAX = 16
WORKSPACE_POINTS_RAD = 10
WORKSPACE_FONT = {'style': 'consolas', 'color': COLOR_BLACK, 'size': 16, 'indent': 4}
CANVAS_FONT = {'style': 'consolas', 'color': COLOR_GRAY, 'size': 32, 'indent': 4}

BSPLINE_DEGREE_MIN = 2
BSPLINE_DEGREE_MAX = 8

PG_FPS = 60