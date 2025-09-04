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
)

window_size = Vector2(800, 420)


class DraggableRectangle:
    def __init__(self, name, x, y, w, h, color=BLUE, min_width=100, max_width=780):
        self.name = name
        self.x = x
        self.y = y
        self.w = max(min(w, max_width), min_width)
        self.h = h
        self.color = color
        self.dragging = False
        self.edge_threshold = 10
        self.min_width = min_width
        self.max_width = max_width
        self.lighter_color = (
            min(color[0] + 40, 255),  # pyright: ignore[reportIndexIssue]
            min(color[1] + 40, 255),  # pyright: ignore[reportIndexIssue]
            min(color[2] + 40, 255),  # pyright: ignore[reportIndexIssue]
            120,
        )

    def on_right_edge(self, mouse_x, mouse_y):
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
                self.lighter_color,
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
        text_x = self.x + 10
        text_y = self.y + 10
        text_size = 10
        text_width = measure_text(self.name, text_size) + 8
        text_height = text_size + 6
        draw_rectangle(text_x - 4, text_y - 2, text_width, text_height, (0, 0, 0, 200))
        draw_text(self.name, text_x, text_y, text_size, WHITE)


rectangles = [
    DraggableRectangle("TL TIMER", 10, 10, 600, 100, RED),
    DraggableRectangle("TL INTERVAL", 10, 110, 300, 100, GREEN),
    DraggableRectangle("EXPOSURE", 10, 210, 120, 100, BLUE),
    DraggableRectangle("PERIOD", 10, 310, 125, 100, PURPLE),
]

init_window(int(window_size.x), int(window_size.y), "timing sim")

while not window_should_close():
    begin_drawing()
    clear_background(WHITE)

    mouse_x = get_mouse_x()
    mouse_y = get_mouse_y()

    for rect in rectangles:
        rect.update(mouse_x, mouse_y)
        rect.draw()

    end_drawing()
close_window()
