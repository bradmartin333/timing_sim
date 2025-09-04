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
    end_drawing,
    close_window,
    Vector2,
    WHITE,
    BLUE,
)

window_size = Vector2(800, 500)

rect_x, rect_y, rect_w, rect_h = 100, 100, 200, 200
edge_threshold = 10
dragging = False

init_window(int(window_size.x), int(window_size.y), "timing sim")

while not window_should_close():
    begin_drawing()
    clear_background(WHITE)

    mouse_x = get_mouse_x()
    mouse_y = get_mouse_y()

    on_right_edge = (
        rect_x + rect_w - edge_threshold <= mouse_x <= rect_x + rect_w + edge_threshold
        and rect_y <= mouse_y <= rect_y + rect_h
    )

    if on_right_edge:
        draw_rectangle(
            rect_x + rect_w - edge_threshold,
            rect_y,
            edge_threshold * 2,
            rect_h,
            (0, 200, 255, 120),
        )

        if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
            dragging = True

    if dragging:
        if is_mouse_button_down(MouseButton.MOUSE_BUTTON_LEFT):
            rect_w = mouse_x - rect_x
        else:
            dragging = False

    draw_rectangle(rect_x, rect_y, rect_w, rect_h, BLUE)

    end_drawing()
close_window()
