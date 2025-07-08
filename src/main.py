import base64
import math
import svgwrite
from svgwrite.shapes import Circle
from string import ascii_lowercase, ascii_uppercase, digits

from src.utils import render_and_save_if_needed, GRID_STEP, LARGE_BLOCK, SMALE_BLOCK, FULL_BLOCK


def generate_letter_svg(letter: str, large: bool = False) -> svgwrite.Drawing:
    """
    Generates an SVG drawing of a single letter.

    Args:
        letter (str): The character to draw.
        large (bool): Whether to use the large grid block or not.

    Returns:
        svgwrite.Drawing: The SVG drawing containing the letter.
    """
    size = LARGE_BLOCK if large else SMALE_BLOCK
    dwg = svgwrite.Drawing(size=(size, size))

    x = size // 2
    y = size // 2 + (size // 5)
    dwg.add(dwg.text(
        letter,
        insert=(x, y),
        text_anchor="middle",
        font_size=str(size // 2),
        font_family="Helmswald Post"
    ))
    return dwg


def generate_msb(letters: str) -> svgwrite.Drawing:
    """
    Generates an MSB (Medium Sigil Block) from 1 to 3 letters.

    Args:
        letters (str): A string with 1 to 3 characters.

    Returns:
        svgwrite.Drawing: The SVG group combining the letter sigils.
    """
    letters_len = len(letters)
    assert 0 < letters_len < 4, "Only 1 to 3 letters are allowed."

    width, height = (SMALE_BLOCK, LARGE_BLOCK) if letters_len == 1 else (FULL_BLOCK, FULL_BLOCK)
    dwg = svgwrite.Drawing(size=(width, height))

    # First (centered) letter
    svg1 = generate_letter_svg(letters[0], large=True)
    group1 = dwg.g()
    for el in svg1.elements:
        group1.add(el)
    group1.translate((width - (GRID_STEP * 3)) // 2, (height - int(GRID_STEP * 3.5)) // 2)
    dwg.add(group1)

    if letters_len > 1:
        svg2 = generate_letter_svg(letters[1], large=False)
        group2 = dwg.g()
        for el in svg2.elements:
            group2.add(el)
        group2.translate(SMALE_BLOCK, SMALE_BLOCK)
        dwg.add(group2)

        if letters_len > 2:
            svg3 = generate_letter_svg(letters[2], large=False)
            group3 = dwg.g()
            for el in svg3.elements:
                group3.add(el)
            group3.translate(0, SMALE_BLOCK)
            dwg.add(group3)

    return dwg


@render_and_save_if_needed(grid=False, save=False)
def generate_bsb(bsb_elems: list, counter: int = 0) -> list:
    """
    Generates BSB (Big Sigil Block) grid from nested MSB groups.

    Args:
        bsb_elems (list): A 2D list of SVG blocks to compose.
        counter (int): Recursion depth (used to calculate scaling).

    Returns:
        list: A list of SVG drawings forming a higher-level sigil.
    """
    base_size = GRID_STEP * 4 * (2 ** counter)
    pos = {
        0: (0, 0),
        1: (0, base_size),
        2: (base_size, 0),
        3: (base_size, base_size)
    }
    dwgs = []
    for ii, bsb_element in enumerate(bsb_elems):
        bsb_len = len(bsb_element)
        width, height = base_size, base_size
        dwg_i = svgwrite.Drawing(size=(width, height))
        if bsb_len > 1:
            dwg_i['height'] = dwg_i['height'] * 2
        if bsb_len > 2:
            dwg_i['width'] = dwg_i['width'] * 2
        for i, bsb in enumerate(bsb_element):
            group = dwg_i.g()
            bsb_elements = bsb.elements
            x, y = pos[i]
            for el in bsb_elements:
                group.add(el)
            rx, ry = x + (base_size // 2), y + (base_size // 2)
            group.rotate(90 * i, (rx, ry))
            group.translate(x, y)
            dwg_i.add(group)
        dwgs.append(dwg_i)

    return dwgs


@render_and_save_if_needed(save=True, grid=False)
def draw_circle(sigil_dwg: svgwrite.Drawing) -> svgwrite.Drawing:
    """
    Wraps an existing SVG drawing with a centered circle.

    Args:
        sigil_dwg (svgwrite.Drawing): The drawing to be wrapped.

    Returns:
        svgwrite.Drawing: A new SVG drawing containing the original drawing and the circle.
    """
    width = float(sigil_dwg.attribs.get('width'))
    height = float(sigil_dwg.attribs.get('height'))
    box_size = max(width, height) + 2
    radius = box_size / 2 - 2
    cx = cy = box_size / 2

    circle = svgwrite.Drawing(size=(box_size, box_size))

    # Draw circle (centered)
    circle_group = circle.g()
    circle_group.add(Circle(center=(cx, cy), r=radius, stroke="black", fill="none", stroke_width=2))
    circle.add(circle_group)

    # Draw sigil content (centered)
    sigil_group = circle.g()
    for el in sigil_dwg.elements:
        sigil_group.add(el)

    sigil_x = cx - width / 2
    sigil_y = cy - height / 2
    sigil_group.translate(sigil_x, sigil_y)
    circle.add(sigil_group)

    return circle


@render_and_save_if_needed()
def draw_def_sigil(input_string: str) -> svgwrite.Drawing:
    """
    Creates a sigil for a Python function name, embedding it inside a pentagram.

    Args:
        input_string (str): A valid Python identifier (e.g., function name).

    Returns:
        svgwrite.Drawing: SVG drawing with the sigil inside a pentagram.
    """
    sigil_dwg = make_sigil(input_string)

    size = sigil_dwg['height'] * 3 + GRID_STEP
    dwg = svgwrite.Drawing(size=(size, size))
    cx, cy = size / 2, size / 2
    radius = size * 0.4

    # Calculate 5 points on the circle
    points = []
    for i in range(5):
        angle_deg = 90 + i * 72
        angle_rad = math.radians(angle_deg)
        x = cx + radius * math.cos(angle_rad)
        y = cy - radius * math.sin(angle_rad)
        points.append((x, y))

    # Draw pentagram using specific connection order
    star_order = [0, 2, 4, 1, 3, 0]
    for i in range(len(star_order) - 1):
        a = points[star_order[i]]
        b = points[star_order[i + 1]]
        dwg.add(dwg.line(start=a, end=b, stroke="black", stroke_width=2))

    group = dwg.g()
    for el in sigil_dwg.elements:
        group.add(el)

    sigil_pos = (size - sigil_dwg['height']) / 2
    group.translate(sigil_pos, sigil_pos)
    dwg.add(group)

    return dwg


@render_and_save_if_needed(save=False, grid=False)
def make_sigil(input_string: str) -> svgwrite.Drawing:
    """
    Creates a full sigil from an identifier string.

    Args:
        input_string (str): A valid Python identifier to encode.

    Returns:
        svgwrite.Drawing: The final SVG sigil drawing.
    """
    if not input_string.isidentifier():
        raise ValueError("Input must be a valid Python identifier.")

    # substrings = [input_string[x * 3:x * 3 + 3] for x in range(math.ceil(len(input_string) / 3))]
    # msb_svgs = [generate_msb(s) for s in substrings]
    # bsb_elems = [msb_svgs[x * 4:x * 4 + 4] for x in range(math.ceil(len(msb_svgs) / 4))]
    # bsb_elems = generate_bsb(bsb_elems)
    #
    # counter = 1
    # while len(bsb_elems) > 1:
    #     bsb_elems = [bsb_elems[x * 4:x * 4 + 4] for x in range(math.ceil(len(bsb_elems) / 4))]
    #     bsb_elems = generate_bsb(bsb_elems, counter)
    #     counter += 1
    bsb_elems = hash_to_svg(in_string)
    sigil = draw_circle(bsb_elems)
    return sigil


def text_to_hash(text: str) -> str:
    """
    Encodes input text into a base32 string without padding.

    Args:
        text (str): Any UTF-8 text.

    Returns:
        str: Base32 encoded string with no trailing '=' characters.
    """
    return base64.b32encode(text.encode('utf-8')).decode('ascii').rstrip('=')


def hash_to_text(hash_string: str) -> str:
    """
    Decodes a base32 string (without padding) back into original text.

    Args:
        hash_string (str): Base32 encoded string without '='.

    Returns:
        str: Decoded original text.
    """
    padding = '=' * (-len(hash_string) % 8)  # base32 requires length % 8 == 0
    decoded_bytes = base64.b32decode(hash_string + padding)
    return decoded_bytes.decode('utf-8')


def draw_custom_path(
    dwg: svgwrite.Drawing,
    start: tuple,
    segments: list,
    size: tuple,
    stroke="black",
    stroke_width=2
) -> svgwrite.path.Path:
    """
    Draws a multi-segment path with optional curves and angle control.

    Args:
        dwg (svgwrite.Drawing): Drawing to add to.
        start (tuple): (x, y) start point.
        segments (list): List of segments, each as:
            {
                "dx": int,
                "dy": int,
                "curved": bool,
                "bend": float (optional, 0–1, curve intensity)
            }
        size (tuple): (width, height) — to constrain the path.
        stroke (str): Stroke color.
        stroke_width (int): Line thickness.

    Returns:
        svgwrite.path.Path: The constructed path.
    """
    width, height = size
    x, y = start
    path = dwg.path(d=f"M {x} {y}", stroke=stroke, fill="none", stroke_width=stroke_width)

    for seg in segments:
        dx = seg["dx"]
        dy = seg["dy"]
        curved = seg.get("curved", False)
        bend = seg.get("bend", 0.5)

        nx = max(0, min(width, x + dx))
        ny = max(0, min(height, y + dy))

        if curved:
            # контрольная точка между (x,y) и (nx,ny) — изогнута перпендикулярно
            cx = x + dx / 2 + bend * dy
            cy = y + dy / 2 - bend * dx
            path.push(f"Q {cx} {cy}, {nx} {ny}")
        else:
            path.push(f"L {nx} {ny}")

        x, y = nx, ny

    return path


def decorate_line_with_perpendiculars(dwg, group, start, end, count=6, length=10, radius=3, spacing=20):
    """
    Decorates a straight line with alternating perpendicular ticks, each ending with a small circle.

    Args:
        dwg (svgwrite.Drawing): SVG drawing to add elements to.
        group (svgwrite.Drawing): SVG drawing to add elements to.
        start (tuple): (x, y) start of main line.
        end (tuple): (x, y) end of main line.
        count (int): Number of decorations (evenly spaced).
        length (int): Length of each perpendicular tick line.
        radius (int): Radius of the circle at the end of each tick.
        spacing (int): Minimum distance between each decoration.
        :param group:
    """
    x0, y0 = start
    x1, y1 = end

    # Main vector
    dx = x1 - x0
    dy = y1 - y0
    length_main = math.hypot(dx, dy)

    if length_main == 0:
        return  # avoid division by zero

    # Unit vector along the main line
    ux = dx / length_main
    uy = dy / length_main

    # Perpendicular unit vector
    px = -uy
    py = ux

    for i in range(1, count + 1):
        # Position along the main line
        t = i / (count + 1)
        base_x = x0 + dx * t
        base_y = y0 + dy * t

        # Alternate direction (+/-) for each decoration
        sign = 1 if i % 2 == 0 else -1

        # Tick end point
        tip_x = base_x + sign * px * length
        tip_y = base_y + sign * py * length

        # Draw tick
        group.add(dwg.line(start=(base_x, base_y), end=(tip_x, tip_y), stroke="black", stroke_width=1))

        # Draw circle
        group.add(dwg.circle(center=(tip_x, tip_y), r=radius,  stroke='black', fill="none", stroke_width=1))


@render_and_save_if_needed(grid=True)
def hash_to_svg(fstring: str) -> svgwrite.Drawing:
    size = GRID_STEP
    min_length = GRID_STEP // 10
    dwg = svgwrite.Drawing(size=(size, size))
    cx, cy = size // 2, size // 2
    x, y = cx, cy
    angle = 0

    for i, char in enumerate(fstring):
        char1, char2 = text_to_hash(char)
        print(char1, char2)
        val1 = ord(char1)
        val2 = ord(char2)
        print(val1, val2)
        is_digit = char.isdigit()
        is_vowels = bool(ord(char) % 2)

        length = min_length + (val1 % 20)
        angle += (val1 % 360)

        rad = math.radians(angle)
        nx = x + length * math.cos(rad)
        ny = y + length * math.sin(rad)

        if not is_digit:
            if is_vowels:
                element = dwg.g()
                start = (x - val1 // 2, y)
                end = (x + val1 // 2, y)
                element.add(dwg.line(start=start, end=end, stroke="black", stroke_width=2))
                decorate_line_with_perpendiculars(
                    dwg,
                    element,
                    start,
                    end,
                    val2 // 10,
                    val2 % 10
                )
                element.rotate(angle, (x, y))

            else:
                segments = [
                    {"dx": val1//10, "dy": 0, "curved": True, "bend": 0.5},
                    {"dx": 0, "dy": val2//10, "curved": True, "bend": -0.4},
                    {"dx": -val1//10, "dy": 0, "curved": True, "bend": 0.5},
                    {"dx": 0, "dy": -val2//10, "curved": True, "bend": -0.5},
                ]
                element = draw_custom_path(dwg, start=(x, y), segments=segments, size=(nx, ny))
        else:
            if is_vowels:
                points = []
                for j in range(3):
                    angle_deg = 60 + j * 120 - 90  # start pointing up
                    angle_rad = math.radians(angle_deg)
                    x = cx + 5 * math.cos(angle_rad)
                    y = cy + 5 * math.sin(angle_rad)
                    points.append((x, y))

                element = dwg.polygon(points=points, fill='black')
            else:
                element = dwg.circle(center=(x, y), r=5, stroke='black', fill="none", stroke_width=1)

        dwg.add(element)

        x, y = nx, ny

    return dwg


if __name__ == "__main__":
    in_string = 'a'
    draw_def_sigil(in_string)



