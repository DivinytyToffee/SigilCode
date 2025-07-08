from functools import wraps
from pathlib import Path


def add_grid(__coord, __grid, dwg):
    height = dwg['height']
    width = dwg['width']
    if __grid:
        for x in range(GRID_STEP, width, GRID_STEP):
            dwg.add(dwg.line(start=(x, 0), end=(x, height), stroke="gray", stroke_dasharray=[5, 5]))
        for y in range(GRID_STEP, height, GRID_STEP):
            dwg.add(dwg.line(start=(0, y), end=(width, y), stroke="gray", stroke_dasharray=[5, 5]))
        if __coord:
            for x in range(GRID_STEP, width, GRID_STEP):
                for y in range(GRID_STEP, height, GRID_STEP):
                    dwg.add(dwg.text(
                        f"({x},{y})",
                        insert=(x + 3, y - 3),
                        font_size="12",
                        fill="gray"
                    ))


def render_and_save_if_needed(__grid=False, __coord=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if not result:
                return result

            bsb = result

            if __grid or __coord:
                add_grid(__coord, __grid, bsb)

            if SAVE:
                output_filename = kwargs.get("input_string")
                output_path = f'output/{output_filename}.svg'
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                bsb.filename = output_path
                bsb.save()

            return result

        return wrapper
    return decorator


GRID_STEP = 100
LARGE_BLOCK = 3 * GRID_STEP
SMALE_BLOCK = 2 * GRID_STEP
FULL_BLOCK = 4 * GRID_STEP
SAVE = True
