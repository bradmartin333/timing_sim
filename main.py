from dataclasses import dataclass
from typing import Any

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
    check_collision_point_rec,
    Vector2,
    WHITE,
    RED,
    GREEN,
    BLUE,
    PURPLE,
    GRAY,
)

# Constants
WINDOW_SIZE = Vector2(800, 420)
EDGE_THRESHOLD = 5
TEXT_SIZE = 10
TEXT_PADDING = 4
ALPHA_LIGHT = 120
ALPHA_BORDER = 50
ALPHA_TEXT_BG = 200
COLOR_BLACK = (0, 0, 0)


@dataclass
class DraggableRectangle:
    name: str
    x: int
    y: int
    w: int
    h: int
    color: Any = BLUE
    min_width: int = 100
    max_width: int = 780
    editable: bool = True
    dragging: bool = False

    def __post_init__(self):
        self.w = max(min(self.w, self.max_width), self.min_width)
        # Handle both tuple and Color types for backward compatibility
        r = (
            getattr(self.color, "r", self.color[0])
            if hasattr(self.color, "r") or isinstance(self.color, tuple)
            else 0
        )
        g = (
            getattr(self.color, "g", self.color[1])
            if hasattr(self.color, "g") or isinstance(self.color, tuple)
            else 0
        )
        b = (
            getattr(self.color, "b", self.color[2])
            if hasattr(self.color, "b") or isinstance(self.color, tuple)
            else 0
        )
        self.lighter_color = (
            min(r + 40, 255),
            min(g + 40, 255),
            min(b + 40, 255),
            ALPHA_LIGHT,
        )

    def on_right_edge(self, mouse_x: int, mouse_y: int) -> bool:
        """Check if mouse is on the right edge of rectangle."""
        if not self.editable:
            return False
        return (
            self.x + self.w - EDGE_THRESHOLD
            <= mouse_x
            <= self.x + self.w + EDGE_THRESHOLD
            and self.y <= mouse_y <= self.y + self.h
        )

    def update(self, mouse_x: int, mouse_y: int) -> None:
        """Update rectangle width based on mouse interaction."""
        if self.on_right_edge(mouse_x, mouse_y):
            # Draw resize handle
            draw_rectangle(
                self.x + self.w - EDGE_THRESHOLD,
                self.y,
                EDGE_THRESHOLD * 2,
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

    def draw(self) -> None:
        """Draw the rectangle with its label."""
        # Draw main rectangle
        draw_rectangle(self.x, self.y, self.w, self.h, self.color)
        draw_rectangle_lines(
            self.x, self.y, self.w, self.h, (*COLOR_BLACK, ALPHA_BORDER)
        )

        # Draw label
        text_x = self.x + 10
        text_y = self.y + 10
        text_width = measure_text(self.name, TEXT_SIZE) + 8
        text_height = TEXT_SIZE + 6

        # Draw label background
        draw_rectangle(
            text_x - TEXT_PADDING,
            text_y - 2,
            text_width,
            text_height,
            (*COLOR_BLACK, ALPHA_TEXT_BG),
        )

        # Draw label text
        draw_text(self.name, text_x, text_y, TEXT_SIZE, WHITE)


def draw_repeated_rectangle(rect: DraggableRectangle, x: int) -> None:
    """Draw a rectangle at the specified x position with border."""
    draw_rectangle(x, rect.y, rect.w, rect.h, rect.lighter_color)
    draw_rectangle_lines(x, rect.y, rect.w, rect.h, (*COLOR_BLACK, ALPHA_BORDER))


# Initialize rectangles
timer_rect = DraggableRectangle("TIMER", 10, 10, 780, 100, RED)
interval_rect = DraggableRectangle("INTERVAL", 10, 110, 300, 100, GREEN)
exposure_rect = DraggableRectangle("EXPOSURE", 10, 210, 120, 100, BLUE, min_width=20)
period_rect = DraggableRectangle(
    "PERIOD", 10, 310, int(120 * 1.03), 100, PURPLE, editable=False
)

# Initialize window
init_window(int(WINDOW_SIZE.x), int(WINDOW_SIZE.y), "timing sim")

# Main loop
while not window_should_close():
    begin_drawing()
    clear_background(WHITE)

    # Get mouse position once per frame
    mouse_x = get_mouse_x()
    mouse_y = get_mouse_y()

    # Update and draw primary rectangles
    timer_rect.update(mouse_x, mouse_y)
    timer_rect.draw()

    # Check for right click within interval rectangle to set width to period
    padded_exposure = exposure_rect.w * 1.03
    if check_collision_point_rec(
        (mouse_x, mouse_y),
        (interval_rect.x, interval_rect.y, interval_rect.w, interval_rect.h),
    ) and is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_RIGHT):
        interval_rect.w = int(padded_exposure)

    # Update interval rectangle constraints and calculate counts
    interval_rect.max_width = timer_rect.w
    interval_rect.update(mouse_x, mouse_y)
    interval_rect.draw()
    num_intervals = int(timer_rect.w / interval_rect.w)

    # Update exposure rectangle constraints
    exposure_rect.max_width = int(interval_rect.w * 0.97)
    exposure_rect.update(mouse_x, mouse_y)
    exposure_rect.draw()

    num_exposures = max(int(interval_rect.w / padded_exposure), 1)

    # Update period rectangle width based on num_exposures
    period_rect.w = int(interval_rect.w / num_exposures)
    period_rect.update(mouse_x, mouse_y)
    period_rect.draw()

    # Update interval minimum width constraint
    interval_rect.min_width = (
        period_rect.w if num_exposures > 1 else int(padded_exposure)
    )

    # Draw repeated intervals and exposures
    for i in range(num_intervals):
        # Skip the first interval as it's already drawn
        if i > 0:
            x = interval_rect.x + i * interval_rect.w
            draw_repeated_rectangle(interval_rect, x)

        # Draw repeated exposures and periods within each interval
        for j in range(num_exposures):
            if i == 0 and j == 0:
                continue  # Skip the first exposure as it's already drawn

            x = interval_rect.x + period_rect.w * j + i * interval_rect.w
            draw_repeated_rectangle(period_rect, x)
            draw_repeated_rectangle(exposure_rect, x)

    end_drawing()

close_window()
