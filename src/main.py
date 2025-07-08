import math
from pathlib import Path

import svgwrite

GRID_STEP = 100
LARGE_BLOCK = 3 * GRID_STEP
SMALE_BLOCK = 2 * GRID_STEP
FULL_BLOCK = 4 * GRID_STEP
SAVE = True


def generate_letter_svg(
        letter: str,
        filename: str = "output.svg",
        large: bool = False,
        __grid: bool = False,
        __coord: bool = False
):
    size = LARGE_BLOCK if large else SMALE_BLOCK
    dwg = svgwrite.Drawing(filename, size=(size, size))

    __add_grid(__coord, __grid, dwg)

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


def generate_msb(
        letters: str,
        filename: str = '',
        __grid: bool = False,
        __coord: bool = False
):
    if not filename:
        filename = f'output/{letters}.svg'
    letters_len = len(letters)
    assert 0 < letters_len < 4, "Only for 1 to 3 letters are allowed"
    width, height = (SMALE_BLOCK, LARGE_BLOCK) if letters_len == 1 else (FULL_BLOCK, FULL_BLOCK)
    dwg = svgwrite.Drawing(filename, size=(width, height))

    svg1 = generate_letter_svg(letters[0], large=True)
    group1 = dwg.g()
    for el in svg1.elements:
        group1.add(el)
    group1.translate((width - (GRID_STEP * 3)) // 2, (height - (int(GRID_STEP * 3.5))) // 2)
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

    __add_grid(__coord, __grid, dwg)
    return dwg


def __add_grid(__coord, __grid, dwg):
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


def generate_bsb(bsb_elems: list, counter: int = 0):
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
            dwg_i['height'] = dwg_i['height']*2
        if bsb_len > 2:
            dwg_i['width'] = dwg_i['width']*2
        for i, bsb in enumerate(bsb_element):
            group = dwg_i.g()
            bsb_elements = bsb.elements
            x, y = pos[i]
            for el in bsb_elements:
                group.add(el)
            rx, ry = x + (base_size//2), y + (base_size//2)
            group.rotate(90*i, (rx, ry))
            group.translate(x, y)
            dwg_i.add(group)
        dwgs.append(dwg_i)

    return dwgs


def make_sigil(input_string, __grid, __coord):
    if not input_string.isidentifier():
        raise ValueError("Строка должна быть допустимым идентификатором Python")
    substrings = [input_string[x * 3:x * 3 + 3] for x in range(math.ceil(len(input_string) / 3))]
    msb_svgs = [generate_msb(s) for s in substrings]
    bsb_elems = [msb_svgs[x * 4:x * 4 + 4] for x in range(math.ceil(len(msb_svgs) / 4))]
    bsb_elems = generate_bsb(bsb_elems)
    counter = 1
    while len(bsb_elems) > 1:
        bsb_elems = [bsb_elems[x * 4:x * 4 + 4] for x in range(math.ceil(len(bsb_elems) / 4))]
        bsb_elems = generate_bsb(bsb_elems, counter)
        counter += 1
    if __grid or __coord or SAVE:
        __add_grid(__coord, __grid, bsb_elems[0])
        if SAVE:
            filename = f'output/{input_string}.svg'
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            bsb_elems[0].filename = filename
            bsb_elems[0].save()
    return bsb_elems[0]


if __name__ == "__main__":
    grid = False
    coord = False
    in_string = 'AbstractFactory'
    make_sigil(in_string, grid, coord)
