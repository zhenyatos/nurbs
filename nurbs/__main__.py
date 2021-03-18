import pygame as pg
import pygame.locals as pl
import nurbs.const as const
import nurbs.core as core

__clocks = None
__screen = None
__canvas = None


def __init():
	global __clocks
	global __screen
	global __canvas

	pg.init()
	pg.display.set_caption(const.WINDOW_CAPTION)

	__clocks = pg.time.Clock()
	__screen = pg.display.set_mode(
		size=const.WINDOW_SIZE)  #, flags=const.WINDOW_FLAGS)
	__canvas = pg.Surface(__screen.get_size()).convert()


def __quit():
	pg.quit()


def main():
	global __clocks
	global __screen
	global __canvas

	__init()

	workspace = core.Workspace(
		const.WORKSPACE_SIZE_X, 
		const.WORKSPACE_SIZE_Y, (
		(__canvas.get_size()[0] - const.WORKSPACE_SIZE_X) // 2, 
		(__canvas.get_size()[1] - const.WORKSPACE_SIZE_Y) // 2))
	canvas_font = pg.font.SysFont(const.CANVAS_FONT['style'], const.CANVAS_FONT['size'])

	run = True
	mouse_button_up = 0
	mouse_button_down = 0
	while run:
		__canvas.fill(const.COLOR_CANVAS)
		__canvas.blit(canvas_font.render('lbutton click: add point', True, const.CANVAS_FONT['color']),
			(const.CANVAS_FONT['indent'], 0))
		__canvas.blit(canvas_font.render('lbutton hold: drag point', True, const.CANVAS_FONT['color']),
			(const.CANVAS_FONT['indent'], const.CANVAS_FONT['size']))
		__canvas.blit(canvas_font.render('rbutton click: remove point', True, const.CANVAS_FONT['color']),
			(const.CANVAS_FONT['indent'], const.CANVAS_FONT['size'] * 2))
		__canvas.blit(canvas_font.render('wheel up/down: inc/dec degree', True, const.CANVAS_FONT['color']),
			(const.CANVAS_FONT['indent'], const.CANVAS_FONT['size'] * 3))

		for event in pg.event.get():
			if event.type == pg.QUIT:
				run = False
			elif event.type == pl.KEYDOWN:
				if event.key == pl.K_ESCAPE:
					run = False
			elif event.type == pl.MOUSEBUTTONUP:
				mouse_button_up = event.button
			elif event.type == pl.MOUSEBUTTONDOWN:
				mouse_button_down = event.button

		pos_mouse = pg.mouse.get_pos()
		workspace.on_mouse_hover(pos_mouse)
		if mouse_button_down:
			workspace.on_mouse_button_down(mouse_button_down)
			mouse_button_down = 0
		if mouse_button_up:
			workspace.on_mouse_button_up(mouse_button_up)
			mouse_button_up = 0

		workspace.draw(__canvas)
		__screen.blit(__canvas, (0, 0))
		pg.display.update()
		__clocks.tick(const.PG_FPS)

	__quit()

if __name__ == '__main__':
	exit(main())
