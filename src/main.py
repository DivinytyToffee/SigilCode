import math
import os
import string
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
    if not input_string.isidentifier():
        raise ValueError("Строка должна быть допустимым идентификатором Python")

    substrings = [input_string[x*3:x*3+3] for x in range(math.ceil(len(input_string) / 3))]
    msb_svgs = [generate_msb(s, __save=False ) for s in substrings]
    bsb_elems = [msb_svgs[x*4:x*4+4] for x in range(math.ceil(len(msb_svgs) / 4))]

    def build_blocks(bsb_element: list, letters: str, count: int = 0):
        n = len(bsb_element)
        multiple = (2 ** count)
        base_size = 400
        if n == 1:
            width, height = base_size * multiple, base_size * multiple
            positions = [(0, 0)]
            rotations = [0]
        elif n == 2:
            width, height = base_size * multiple, 2 * base_size * multiple
            positions = [
                (0, 0),
                (0, base_size * multiple),
            ]
            rotations = [0, 90]
        elif n == 3:
            width, height = 2 * base_size * multiple, 2 * base_size * multiple
            positions = [
                (base_size * multiple, 0),
                (base_size * multiple, base_size * multiple),
                (0, base_size * multiple),
            ]
            rotations = [0, 90, 180]
        elif n == 4:
            width, height = 2 * base_size * multiple, 2 * base_size * multiple
            positions = [
                (base_size * multiple, 0),
                (base_size * multiple, base_size * multiple),
                (0, base_size * multiple),
                (0, 0),
            ]
            rotations = [0, 90, 180, 270]
        else:
            groups = [bsb_element[i:i+4] for i in range(0, n, 4)]
            group_letters = [letters[i*4:(i+1)*4] for i in range(math.ceil(n/4))]
            sub_svgs = []
            for idx, (group, group_let) in enumerate(zip(groups, group_letters)):
                svg, _, _ = build_blocks(group, group_let, count+1)
                sub_svgs.append(svg)
            return build_blocks(sub_svgs, letters, count)
        dwg_i = svgwrite.Drawing(f"output/{letters}_{count}.svg", size=(width, height))
        for i, bsb in enumerate(bsb_element):
            group = dwg_i.g()
            for el in bsb.elements:
                group.add(el)
            x, y = positions[i]
            angle = rotations[i]
            cx = x + base_size * multiple // 2
            cy = y + base_size * multiple // 2
            if angle != 0:
                group.rotate(angle, (cx, cy))
            group.translate(x, y)
            dwg_i.add(group)
        return dwg_i, width, height

    def compose_bsb(nabor, letters_list, count: int = 0):
        ret_nabor = []
        ret_letters = []
        for bsbs, letters in zip(nabor, letters_list):
            if bsbs:
                svg, width, height = build_blocks(bsbs, letters, count)
                ret_nabor.append(svg)
                ret_letters.append(letters)
        return ret_nabor, ret_letters, width, height

    count = -1
    letters_list = [s for s in substrings]
    i = len(bsb_elems[0])
    while i > 1:
        count += 1
        i -= 1
        a, letters_list, width, height = compose_bsb(bsb_elems, letters_list, count)
        bsb_elems = [a]

    final_svg = bsb_elems[0][0]

    if __grid or __coord:
        __add_grid(__coord, __grid, final_svg, height, width)
    if __save:
        out_path = filename if filename else 'output/final.svg'
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        final_svg.save(out_path)
    return final_svg


if __name__ == "__main__":
    generate(string.ascii_uppercase + string.ascii_letters[:23], __grid=True, __coord=True, __save=True)
