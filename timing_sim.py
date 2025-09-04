# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "raylib>=5.5.0.3",
# ]
# ///

from dataclasses import dataclass
from typing import Any

from pyray import (
    init_window,
    window_should_close,
    set_config_flags,
    set_window_title,
    ConfigFlags,
    begin_drawing,
    clear_background,
    get_mouse_position,
    is_mouse_button_pressed,
    is_mouse_button_down,
    MouseButton,
    draw_rectangle_rec,
    draw_line_v,
    measure_text,
    draw_text,
    end_drawing,
    close_window,
    check_collision_point_rec,
    Vector2,
    Rectangle,
    WHITE,
    RED,
    GREEN,
    BLUE,
    PURPLE,
    GRAY,
    BLACK,
)

# Constants
WINDOW_SIZE = Vector2(800, 440)
EDGE_THRESHOLD = 10
TEXT_SIZE = 10
TEXT_PADDING = 4
LINE_WIDTH = 1.0
EXPOSURE_PADDING = 0.03
EXPOSURE_DOWNSCALE = 1.0 - EXPOSURE_PADDING
MIN_PERIOD = 50


def draw_accurate_border(rect: Rectangle) -> None:
    draw_line_v(Vector2(rect.x, rect.y), Vector2(rect.x, rect.y + rect.height), BLACK)
    draw_line_v(
        Vector2(rect.x + rect.width, rect.y),
        Vector2(rect.x + rect.width, rect.y + rect.height),
        BLACK,
    )
    draw_line_v(Vector2(rect.x, rect.y), Vector2(rect.x + rect.width, rect.y), BLACK)
    draw_line_v(
        Vector2(rect.x, rect.y + rect.height),
        Vector2(rect.x + rect.width, rect.y + rect.height),
        BLACK,
    )


@dataclass
class DraggableRectangle:
    name: str
    x: float
    y: float
    w: float
    h: float
    color: Any = BLUE
    min_width: float = 20.0
    max_width: float = 780.0
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
        self.lighter_color = (min(r + 40, 255), min(g + 40, 255), min(b + 40, 255), 120)

    def get_rect(self) -> Rectangle:
        return Rectangle(self.x, self.y, self.w, self.h)

    def on_right_edge(self, mouse: Vector2) -> bool:
        """Check if mouse is on the right edge of rectangle."""
        if not self.editable:
            return False
        return (
            self.x + self.w - EDGE_THRESHOLD
            <= mouse.x
            <= self.x + self.w + EDGE_THRESHOLD
            and self.y <= mouse.y <= self.y + self.h
        )

    def update(self, mouse: Vector2) -> None:
        """Update rectangle width based on mouse interaction."""
        if self.on_right_edge(mouse):
            self.hover = True
            if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
                self.dragging = True
        else:
            self.hover = False

        if self.dragging:
            if is_mouse_button_down(MouseButton.MOUSE_BUTTON_LEFT):
                new_width = mouse.x - self.x
                self.w = max(self.min_width, min(new_width, self.max_width))
            else:
                self.dragging = False

    def draw(self) -> None:
        """Draw the rectangle with its label."""
        # Draw main rectangle
        r = self.get_rect()
        draw_rectangle_rec(r, self.color)
        draw_accurate_border(r)

        # Draw label
        text_x = self.x + 10
        text_y = self.y + 10
        text_width = measure_text(self.name, TEXT_SIZE) + 8
        text_height = TEXT_SIZE + 6

        # Draw resize handle
        if self.hover or self.dragging:
            draw_rectangle_rec(
                Rectangle(
                    self.x + self.w - EDGE_THRESHOLD, self.y, EDGE_THRESHOLD, self.h
                ),
                GRAY,
            )

        # Draw label background
        draw_rectangle_rec(
            Rectangle(text_x - TEXT_PADDING, text_y - 2, text_width, text_height),
            BLACK,
        )

        # Draw label text
        draw_text(self.name, int(text_x), int(text_y), TEXT_SIZE, WHITE)


# Initialize rectangles
timer_rect = DraggableRectangle("TIMER", 10.0, 10.0, 780.0, 100.0, RED)
interval_rect = DraggableRectangle("INTERVAL", 10.0, 110.0, 300.0, 100.0, GREEN)
exposure_rect = DraggableRectangle(
    "EXPOSURE",
    10.0,
    210.0,
    (120.0 * EXPOSURE_DOWNSCALE),
    100.0,
    BLUE,
    min_width=(20.0 * EXPOSURE_DOWNSCALE),
)
period_rect = DraggableRectangle(
    "PERIOD", 10.0, 330.0, 120.0, 100.0, PURPLE, editable=False
)


def draw_repeated_rectangle(rect: DraggableRectangle, x: float) -> None:
    """Draw a rectangle at the specified x position with border."""
    r = Rectangle(x, rect.y, rect.w, rect.h)
    draw_rectangle_rec(r, rect.lighter_color)
    draw_accurate_border(r)


def padded_exposure() -> float:
    return exposure_rect.w * (1.0 + EXPOSURE_PADDING)


# Initialize window
set_config_flags(ConfigFlags.FLAG_MSAA_4X_HINT)
init_window(int(WINDOW_SIZE.x), int(WINDOW_SIZE.y), "timing sim")

# Main loop
idle_time_infraction = False
while not window_should_close():
    begin_drawing()
    clear_background(RED if idle_time_infraction else WHITE)

    # Get mouse position once per frame
    mouse = get_mouse_position()

    # Check if timer is decreasing past interval
    if timer_rect.w < interval_rect.w:
        interval_rect.w = timer_rect.w
        interval_rect.update(mouse)
    # Check if interval is increasing past timer
    if interval_rect.w > timer_rect.w:
        timer_rect.w = interval_rect.w
    timer_rect.update(mouse)

    # Check for right click within interval rectangle to set width to period
    if check_collision_point_rec(
        mouse, interval_rect.get_rect()
    ) and is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_RIGHT):
        interval_rect.w = padded_exposure()

    # Update interval rectangle constraints and calculate counts
    interval_rect.update(mouse)

    # Update exposure rectangle constraints
    exposure_rect.max_width = interval_rect.max_width * EXPOSURE_DOWNSCALE
    exposure_rect.update(mouse)

    functional_exposure = max(padded_exposure(), MIN_PERIOD)
    num_exposures = max(int(interval_rect.w / functional_exposure), 1)
    set_window_title(
        f"{num_exposures - 1} skipped frame{"" if num_exposures == 2 else "s"}"
    )
    if num_exposures == 1:
        # Check if interval is decreasing past exposure
        if interval_rect.w < padded_exposure():
            exposure_rect.w = interval_rect.w * EXPOSURE_DOWNSCALE
            exposure_rect.update(mouse)
        # Check if exposure is increasing past interval
        if padded_exposure() > interval_rect.w:
            interval_rect.w = padded_exposure()
            # Check if interval is increasing past timer
            if interval_rect.w > timer_rect.w:
                timer_rect.w = interval_rect.w
                timer_rect.update(mouse)
            interval_rect.update(mouse)

    # Update period rectangle width based on num_exposures
    period_rect.w = interval_rect.w / num_exposures
    total_period = period_rect.w * num_exposures
    period_gap = interval_rect.w - total_period
    period_rect.update(mouse)

    # Draw repeated intervals and exposures
    num_intervals = int(timer_rect.w / interval_rect.w)
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

    # Draw core rectangles
    timer_rect.draw()
    interval_rect.draw()
    exposure_rect.draw()
    period_rect.draw()

    # Calculate sensor idle time
    idle_time = period_rect.w - exposure_rect.w
    idle_fraction = idle_time / timer_rect.w
    idle_time_infraction = (
        idle_fraction > 0.25
    )  # This would be some actual number of µs
    timer_rect.name = (
        "***SENSOR IDLE TIME INFRACTION***" if idle_time_infraction else "TIMER"
    )

    end_drawing()

close_window()
