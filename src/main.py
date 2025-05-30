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
    dwg.save()
    print(f"SVG with letter '{letter}' saved as {filename} ({size}x{size})")
    if __save:
        dwg.save()
    return dwg


def generate_composite_svg(
        letters: str,
        filename: str = "output/composite.svg",
        __grid: bool = False,
        __coord: bool = False,
        __save: bool = True
):
    letters_len = len(letters)
    print(letters_len)
    assert 0 < letters_len < 4, "Only for 1 to 3 letters are allowed"
    width, height = 500, 300
    dwg = svgwrite.Drawing(filename, size=(width, height))

    svg1 = generate_letter_svg(letters[0], __save=__save, large=True, __grid=__grid, __coord=__coord)
    group1 = dwg.g()
    for el in svg1.elements:
        group1.add(el)
    group1.translate((width - 300) // 2, (height - 300) // 2)
    dwg.add(group1)

    if letters_len > 1:
        svg2 = generate_letter_svg(letters[1], __save=__save, large=False, __grid=__grid, __coord=__coord)
        group2 = dwg.g()
        for el in svg2.elements:
            group2.add(el)
        group2.translate(300, 100)
        dwg.add(group2)

        if letters_len > 2:
            svg3 = generate_letter_svg(letters[2], __save=__save, large=False, __grid=__grid, __coord=__coord)
            group3 = dwg.g()
            for el in svg3.elements:
                group3.add(el)
            group3.translate(0, 100)
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




if __name__ == "__main__":
    letter = 'B'
    large = True
    filename = f"output/letter_{letter}_{'large' if large else 'small'}.svg"
    generate_letter_svg(letter, filename, large=large)
    letter = 'B'
    large = False
    filename = f"output/letter_{letter}_{'large' if large else 'small'}.svg"
    generate_letter_svg(letter, filename, large=large)
