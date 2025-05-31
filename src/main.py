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


def generate_composite_svg(
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


def generate_superblock(
    input_string: str,
    filename: str = "output/superblock.svg",
    __grid: bool = False,
    __coord: bool = False,
    __save: bool = True
):
    # Проверка допустимости идентификатора
    if not input_string.isidentifier():
        raise ValueError("Строка должна быть допустимым идентификатором Python")

    # # Корректное разбиение на подстроки по 3, 2 или 1 символу
    # substrings = []
    # i = 0
    # n = len(input_string)
    # while i < n:
    #     remain = n - i
    #     if remain == 4:
    #         substrings.append(input_string[i:i+2])
    #         substrings.append(input_string[i+2:i+4])
    #         break
    #     elif remain == 5:
    #         substrings.append(input_string[i:i+3])
    #         substrings.append(input_string[i+3:i+5])
    #         break
    #     elif remain >= 3:
    #         substrings.append(input_string[i:i+3])
    #         i += 3
    #     else:
    #         substrings.append(input_string[i:])
    #         break
    #     i = len(''.join(substrings))
    #
    # # Генерируем МСБ для каждой подстроки
    # msb_svgs = [generate_composite_svg(s, __grid=__grid, __coord=__coord, __save=False) for s in substrings]
    #
    # # Применяем поворот к нужным МСБ заранее (пример: для случая из двух МСБ)
    # def apply_pre_rotation(blocks):
    #     new_blocks = []
    #     i = 0
    #     while i < len(blocks):
    #         # Если осталось два блока, второй поворачиваем на 180°
    #         if i + 1 < len(blocks) and len(blocks) - i == 2:
    #             new_blocks.append(blocks[i])
    #             # Поворачиваем второй МСБ на 180°
    #             size = (int(blocks[i+1]['width']), int(blocks[i+1]['height']))
    #             dwg = svgwrite.Drawing(size=size, profile='tiny')
    #             g = dwg.g()
    #             for el in blocks[i+1].elements:
    #                 g.add(el)
    #             g.rotate(180, center=(0, 0))
    #             dwg.add(g)
    #             new_blocks.append(dwg)
    #             break
    #         else:
    #             new_blocks.append(blocks[i])
    #         i += 1
    #     return new_blocks
    #
    # msb_svgs = apply_pre_rotation(msb_svgs)
    #
    # # Рекурсивная сборка БСБ
    # def build_blocks(blocks, block_size):
    #     msb_w, msb_h = 500, 300
    #     if len(blocks) == 1:
    #         return blocks[0], block_size
    #     grouped = [blocks[i:i+4] for i in range(0, len(blocks), 4)]
    #     new_blocks = []
    #     for group in grouped:
    #         if len(group) == 2:
    #             # 2 МСБ: итоговый SVG 500x700, первый сверху, второй снизу, оба центрированы по горизонтали
    #             dwg = svgwrite.Drawing(size=(msb_w, msb_h * 2 + 100))
    #             g1 = dwg.g()
    #             for el in group[0].elements:
    #                 g1.add(el)
    #             g1.translate(0, 0)
    #             dwg.add(g1)
    #             g2 = dwg.g()
    #             for el in group[1].elements:
    #                 g2.add(el)
    #             g2.translate(0, msb_h + 100)
    #             dwg.add(g2)
    #             new_blocks.append(dwg)
    #         elif len(group) == 3:
    #             # 3 МСБ: итоговый SVG 800x700, два сверху (слева и справа), третий снизу по центру
    #             dwg = svgwrite.Drawing(size=(msb_w + msb_w//2, msb_h * 2 + 100))
    #             # Первый слева сверху
    #             g1 = dwg.g()
    #             for el in group[0].elements:
    #                 g1.add(el)
    #             g1.translate(0, 0)
    #             dwg.add(g1)
    #             # Второй справа сверху
    #             g2 = dwg.g()
    #             for el in group[1].elements:
    #                 g2.add(el)
    #             g2.translate(msb_w//2 + msb_w, 0)
    #             g2.translate(-msb_w, 0)  # чтобы правый край совпал с правым краем SVG
    #             dwg.add(g2)
    #             # Третий снизу по центру
    #             g3 = dwg.g()
    #             for el in group[2].elements:
    #                 g3.add(el)
    #             g3.translate((dwg['width'] - msb_w)//2, msb_h + 100)
    #             dwg.add(g3)
    #             new_blocks.append(dwg)
    #         else:
    #             # 4 МСБ: второй МСБ развёрнут на 90 градусов относительно первого, остальные без поворота
    #             new_size = block_size * 2
    #             dwg = svgwrite.Drawing(size=(new_size, new_size))
    #             # Первый МСБ — без изменений, центрируется в квадрате
    #             g1 = dwg.g()
    #             for el in group[0].elements:
    #                 g1.add(el)
    #             x1 = (new_size - msb_w) // 2
    #             y1 = (new_size - msb_h) // 2
    #             g1.translate(x1, y1)
    #             dwg.add(g1)
    #             # Второй МСБ — только поворот на 90°, без центрирования
    #             if len(group) > 1:
    #                 g2 = dwg.g()
    #                 for el in group[1].elements:
    #                     g2.add(el)
    #                 g2.rotate(180, center=(0, 0))
    #                 g2.translate(x1, y1)
    #                 dwg.add(g2)
    #             # Третий МСБ — без поворота, позиционируем чтобы (100,300) c касался (200,300) a
    #             if len(group) > 2:
    #                 g3 = dwg.g()
    #                 for el in group[2].elements:
    #                     g3.add(el)
    #                 x3 = x1 + 200 - 100
    #                 y3 = y1 + 300 - 300
    #                 g3.translate(x3, y3)
    #                 dwg.add(g3)
    #             # Четвёртый МСБ — без поворота, позиционируем чтобы (100,300) d касался (100,300) a
    #             if len(group) > 3:
    #                 g4 = dwg.g()
    #                 for el in group[3].elements:
    #                     g4.add(el)
    #                 x4 = x1 + 100 - 100
    #                 y4 = y1 + 300 - 300
    #                 g4.translate(x4, y4)
    #                 dwg.add(g4)
    #             new_blocks.append(dwg)
    #     # Для следующего уровня блок_size должен быть равен размеру текущего блока
    #     next_block_size = int(new_blocks[0]['width']) if new_blocks else block_size * 2
    #     return build_blocks(new_blocks, next_block_size)
    #
    # final_svg, final_size = build_blocks(msb_svgs, 500)
    # if __grid or __coord:
    #     __add_grid(__coord, __grid, final_svg, final_size, final_size)
    # if __save:
    #     final_svg.saveas(filename)
    # return final_svg


if __name__ == "__main__":
    generate_composite_svg("W", __grid=True, __coord=True, __save=True)
    generate_composite_svg("WW", __grid=True, __coord=True, __save=True)
    generate_composite_svg("WWW", __grid=True, __coord=True, __save=True)
