from collections.abc import Iterable
from functools import wraps
from pathlib import Path
import svgwrite

# Grid constants
GRID_STEP = 100
LARGE_BLOCK = 3 * GRID_STEP
SMALE_BLOCK = 2 * GRID_STEP
FULL_BLOCK = 4 * GRID_STEP


def add_grid(coord: bool, grid: bool, dwg: svgwrite.Drawing) -> None:
    """
    Adds a grid and optional coordinate labels to an SVG drawing.

    Args:
        coord (bool): Whether to draw coordinate labels at each grid point.
        grid (bool): Whether to draw grid lines.
        dwg (svgwrite.Drawing): The SVG object to modify.
    """
    height = float(dwg['height'])
    width = float(dwg['width'])

    if grid:
        # Draw vertical lines
        for x in range(GRID_STEP, int(width), GRID_STEP):
            dwg.add(dwg.line(
                start=(x, 0),
                end=(x, height),
                stroke="gray",
                stroke_dasharray=[5, 5]
            ))

        # Draw horizontal lines
        for y in range(GRID_STEP, int(height), GRID_STEP):
            dwg.add(dwg.line(
                start=(0, y),
                end=(width, y),
                stroke="gray",
                stroke_dasharray=[5, 5]
            ))

        # Add coordinates at grid intersections
        if coord:
            for x in range(GRID_STEP, int(width), GRID_STEP):
                for y in range(GRID_STEP, int(height), GRID_STEP):
                    dwg.add(dwg.text(
                        f"({x},{y})",
                        insert=(x + 3, y - 3),
                        font_size="12",
                        fill="gray"
                    ))


def render_and_save_if_needed(grid: bool = False, coord: bool = False, save: bool = True):
    """
    A decorator that optionally adds a grid and saves the result as an SVG file.

    Args:
        grid (bool): If True, draw grid lines.
        coord (bool): If True, include coordinate labels at each grid intersection.
        save (bool): If True, save in file.

    Returns:
        Callable: A wrapped function that adds the grid and saves the SVG file.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if not result:
                return result

            bsb = result[-1] if isinstance(result, Iterable) else result

            if grid or coord:
                add_grid(coord, grid, bsb)

            if save:
                output_filename = kwargs.get("input_string", func.__name__)
                output_path = f'output/{output_filename}.svg'
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                bsb.filename = output_path
                bsb.save()

            return result

        return wrapper
    return decorator
