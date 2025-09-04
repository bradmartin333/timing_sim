from pyray import (
    init_window,
    window_should_close,
    begin_drawing,
    clear_background,
    get_mouse_x,
    get_mouse_y,
    is_mouse_button_pressed,
    is_mouse_button_down,
    MouseButton,
    draw_rectangle,
    draw_rectangle_lines,
    measure_text,
    draw_text,
    end_drawing,
    close_window,
    Vector2,
    WHITE,
    RED,
    GREEN,
    BLUE,
    PURPLE,
    GRAY,
)

window_size = Vector2(800, 420)


class DraggableRectangle:
    def __init__(
        self, name, x, y, w, h, color=BLUE, min_width=100, max_width=780, editable=True
    ):
        self.name = name
        self.x = x
        self.y = y
        self.w = max(min(w, max_width), min_width)
        self.h = h
        self.color = color
        self.dragging = False
        self.edge_threshold = 5
        self.min_width = min_width
        self.max_width = max_width
        self.editable = editable
        self.lighter_color = (
            min(color[0] + 40, 255),  # pyright: ignore[reportIndexIssue]
            min(color[1] + 40, 255),  # pyright: ignore[reportIndexIssue]
            min(color[2] + 40, 255),  # pyright: ignore[reportIndexIssue]
            120,
        )

    def on_right_edge(self, mouse_x, mouse_y):
        if not self.editable:
            return False
        return (
            self.x + self.w - self.edge_threshold
            <= mouse_x
            <= self.x + self.w + self.edge_threshold
            and self.y <= mouse_y <= self.y + self.h
        )

    def update(self, mouse_x, mouse_y):
        if self.on_right_edge(mouse_x, mouse_y):
            draw_rectangle(
                self.x + self.w - self.edge_threshold,
                self.y,
                self.edge_threshold * 2,
                self.h,
                GRAY,
            )
            if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
                self.dragging = True

        if self.dragging:
            if is_mouse_button_down(MouseButton.MOUSE_BUTTON_LEFT):
                new_width = mouse_x - self.x
                self.w = max(self.min_width, min(new_width, self.max_width))
            else:
                self.dragging = False

    def draw(self):
        draw_rectangle(self.x, self.y, self.w, self.h, self.color)
        draw_rectangle_lines(self.x, self.y, self.w, self.h, (0, 0, 0, 50))
        text_x = self.x + 10
        text_y = self.y + 10
        text_size = 10
        text_width = measure_text(self.name, text_size) + 8
        text_height = text_size + 6
        draw_rectangle(text_x - 4, text_y - 2, text_width, text_height, (0, 0, 0, 200))
        draw_text(self.name, text_x, text_y, text_size, WHITE)


timer_rect = DraggableRectangle("TIMER", 10, 10, 780, 100, RED)
interval_rect = DraggableRectangle("INTERVAL", 10, 110, 300, 100, GREEN)
exposure_rect = DraggableRectangle("EXPOSURE", 10, 210, 120, 100, BLUE, min_width=20)
period_rect = DraggableRectangle(
    "PERIOD", 10, 310, int(120 * 1.03), 100, PURPLE, editable=False
)

init_window(int(window_size.x), int(window_size.y), "timing sim")

while not window_should_close():
    begin_drawing()
    clear_background(WHITE)

    mouse_x = get_mouse_x()
    mouse_y = get_mouse_y()

    timer_rect.update(mouse_x, mouse_y)
    timer_rect.draw()

    interval_rect.max_width = timer_rect.w
    interval_rect.update(mouse_x, mouse_y)
    interval_rect.draw()
    num_intervals = int(timer_rect.w / interval_rect.w)

    exposure_rect.max_width = int(interval_rect.w * 0.97)
    exposure_rect.update(mouse_x, mouse_y)
    exposure_rect.draw()
    padded_exposure = exposure_rect.w * 1.03
    num_exposures = max(int(interval_rect.w / padded_exposure), 1)

    period_rect.w = int(float(interval_rect.w) / num_exposures)
    period_rect.update(mouse_x, mouse_y)
    period_rect.draw()

    interval_rect.min_width = (
        period_rect.w if num_exposures > 1 else int(padded_exposure)
    )

    for i in range(num_intervals):
        x = interval_rect.x + i * interval_rect.w

        if i > 0:
            draw_rectangle(
                x,
                interval_rect.y,
                interval_rect.w,
                interval_rect.h,
                interval_rect.lighter_color,
            )
            draw_rectangle_lines(
                x, interval_rect.y, interval_rect.w, interval_rect.h, (0, 0, 0, 50)
            )

        for j in range(num_exposures):
            if i == 0 and j == 0:
                continue

            x = interval_rect.x + period_rect.w * j + i * interval_rect.w
            draw_rectangle(
                x,
                period_rect.y,
                period_rect.w,
                period_rect.h,
                period_rect.lighter_color,
            )
            draw_rectangle_lines(
                x, period_rect.y, period_rect.w, period_rect.h, (0, 0, 0, 50)
            )
            draw_rectangle(
                x,
                exposure_rect.y,
                exposure_rect.w,
                exposure_rect.h,
                exposure_rect.lighter_color,
            )
            draw_rectangle_lines(
                x, exposure_rect.y, exposure_rect.w, exposure_rect.h, (0, 0, 0, 50)
            )

    end_drawing()
close_window()
