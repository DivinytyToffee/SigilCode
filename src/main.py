import math
import os
from pathlib import Path

import svgwrite


def generate_letter_svg(
        letter: str,
        filename: str = "output.svg",
        large: bool = False,
        __grid: bool = False,
        __coord: bool = False,
        __save: bool = True
):
    size = 300 if large else 200
    dwg = svgwrite.Drawing(filename, size=(size, size))

    __add_grid(__coord, __grid, dwg, size, size)

    x = size // 2
    y = size // 2 + (size // 5)
    dwg.add(dwg.text(
        letter,
        insert=(x, y),
        text_anchor="middle",
        font_size=str(size // 2),
        font_family="Helmswald Post"
    ))
    if __save:
        dwg.save()
    return dwg


def generate_msb(
        letters: str,
        filename: str = '',
        __grid: bool = False,
        __coord: bool = False,
        __save: bool = True
):
    if not filename:
        filename = f'output/{letters}.svg'
    letters_len = len(letters)
    assert 0 < letters_len < 4, "Only for 1 to 3 letters are allowed"
    width, height = (200, 300) if letters_len == 1 else (400, 400)
    dwg = svgwrite.Drawing(filename, size=(width, height))

    svg1 = generate_letter_svg(letters[0], __save=False, large=True)
    group1 = dwg.g()
    for el in svg1.elements:
        group1.add(el)
    group1.translate((width - 300) // 2, (height - 350) // 2)
    dwg.add(group1)

    if letters_len > 1:
        svg2 = generate_letter_svg(letters[1], __save=False, large=False)
        group2 = dwg.g()
        for el in svg2.elements:
            group2.add(el)
        group2.translate(200, 200)
        dwg.add(group2)

        if letters_len > 2:
            svg3 = generate_letter_svg(letters[2], __save=False, large=False)
            group3 = dwg.g()
            for el in svg3.elements:
                group3.add(el)
            group3.translate(0, 200)
            dwg.add(group3)

    __add_grid(__coord, __grid, dwg, height, width)

    if __save:
        dwg.save()
    return dwg


def __add_grid(__coord, __grid, dwg, height, width):
    if __grid:
        for x in range(100, width, 100):
            dwg.add(dwg.line(start=(x, 0), end=(x, height), stroke="gray", stroke_dasharray=[5, 5]))
        for y in range(100, height, 100):
            dwg.add(dwg.line(start=(0, y), end=(width, y), stroke="gray", stroke_dasharray=[5, 5]))
        if __coord:
            for x in range(100, width, 100):
                for y in range(100, height, 100):
                    dwg.add(dwg.text(
                        f"({x},{y})",
                        insert=(x + 3, y - 3),
                        font_size="12",
                        fill="gray"
                    ))


def generate(
    input_string: str,
    filename: str = "output/superblock.svg",
    __grid: bool = False,
    __coord: bool = False,
    __save: bool = True
):
    # Проверка допустимости идентификатора
    if not input_string.isidentifier():
        raise ValueError("Строка должна быть допустимым идентификатором Python")

    substrings = [input_string[x*3:x*3+3] for x in range(math.ceil(len(input_string) / 3))]
    msb_svgs = [generate_msb(s, __save=True) for s in substrings]
    bsb_elems = [msb_svgs[x*4:x*4+4] for x in range(math.ceil(len(msb_svgs) / 4))]

    def build_blocks(bsb_element: list, count: int = 0):
        bsb_len = len(bsb_element)
        multiple = (2 ** count)
        if bsb_len == 1:
            width, height = 400 * multiple, 400 * multiple
        elif bsb_len == 2:
            width, height = 400 * multiple, 800 * multiple
        else:
            width, height = 800 * multiple, 800 * multiple
        dwg_i = svgwrite.Drawing(f"output/{''.join(substrings[0:bsb_len])}_{count}.svg", size=(width, height))
        pos = {
                0: (400, 0),
                1: (400, 400),
                2: (0, 400),
                3: (0, 0),
            }

        for i, bsb in enumerate(bsb_element):
            group = dwg_i.g()
            for el in bsb.elements:
                group.add(el)
            x, y = pos[i]
            rx, ry = x + 200, y + 200
            group.rotate(90*i, (rx, ry))
            group.translate(x, y)
            dwg_i.add(group)

        dwg_i.save()

        return dwg_i, width, height

    def compose_bsb(nabor, count: int = 0):
        ret_nabor = []
        for bsbs in nabor:
            if bsbs:
                svg, width, height = build_blocks(bsbs, count)
                ret_nabor.append(svg)
        return ret_nabor, width, height

    count = -1
    i = len(bsb_elems[0])
    while i > 1:
        count += 1
        i -= 1
        a, width, height = compose_bsb(bsb_elems, count)
        bsb_elems = [a]

    final_svg = bsb_elems[0][0]

    if __grid or __coord:
        __add_grid(__coord, __grid, final_svg, height, width)
    if __save:
        final_svg.save()
    return final_svg


if __name__ == "__main__":
    generate("ABCDEFGHIGKLOMNPQRST", __grid=True, __coord=True, __save=True)
