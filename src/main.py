import math
import svgwrite
from svgwrite.shapes import Circle

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


def generate_bsb(bsb_elems: list, counter: int = 0) -> list:
    """
    Generates BSB (Big Sigil Block) grid from nested MSB groups.

    Args:
        bsb_elems (list): A 2D list of SVG blocks to compose.
        counter (int): Recursion depth (used to calculate scaling).

    Returns:
        list: A list of SVG drawings forming a higher-level sigil.
    """
    base_size = 400 * (2 ** counter)
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


def draw_circle(sigil_dwg: svgwrite.Drawing, padding: int = 20) -> svgwrite.Drawing:
    """
    Wraps an existing SVG drawing with a centered circle.

    Args:
        sigil_dwg (svgwrite.Drawing): The drawing to be wrapped.
        padding (int): Padding around the drawing before circle.

    Returns:
        svgwrite.Drawing: A new SVG drawing containing the original drawing and the circle.
    """
    width = float(sigil_dwg.attribs.get('width'))
    height = float(sigil_dwg.attribs.get('height'))
    box_size = max(width, height) + padding * 2
    radius = box_size / 2
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
def draw_def_sigil(sigil_dwg: svgwrite.Drawing):
    size: int = sigil_dwg['height'] * 4 + 150
    dwg = svgwrite.Drawing(size=(size, size))
    cx, cy = size / 2, size / 2
    radius = size * 0.4  # leave padding

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
        dwg.add(dwg.line(start=a, end=b, stroke="black", stroke_width=10))

    group = dwg.g()
    for el in sigil_dwg.elements:
        group.add(el)
    sigil_x = cx / 1.325
    sigil_y = cy / 1.325
    group.translate(sigil_x, sigil_y)
    dwg.add(group)

    return dwg


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

    substrings = [input_string[x * 3:x * 3 + 3] for x in range(math.ceil(len(input_string) / 3))]
    msb_svgs = [generate_msb(s) for s in substrings]
    bsb_elems = [msb_svgs[x * 4:x * 4 + 4] for x in range(math.ceil(len(msb_svgs) / 4))]
    bsb_elems = generate_bsb(bsb_elems)

    counter = 1
    while len(bsb_elems) > 1:
        bsb_elems = [bsb_elems[x * 4:x * 4 + 4] for x in range(math.ceil(len(bsb_elems) / 4))]
        bsb_elems = generate_bsb(bsb_elems, counter)
        counter += 1

    sigil = draw_circle(bsb_elems[0])
    return sigil


if __name__ == "__main__":
    in_string = 'AbstractFactory'
    sigil_text = make_sigil(in_string)
    draw_def_sigil(sigil_text)
