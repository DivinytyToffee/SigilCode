import svgwrite


def generate_letter_svg(letter: str, filename: str = "output.svg", large: bool = False):
    size = 300 if large else 200
    dwg = svgwrite.Drawing(filename, size=(size, size))

    for x in range(100, size, 100):
        dwg.add(dwg.line(start=(x, 0), end=(x, size), stroke="gray", stroke_dasharray=[5, 5]))
    for y in range(100, size, 100):
        dwg.add(dwg.line(start=(0, y), end=(size, y), stroke="gray", stroke_dasharray=[5, 5]))

    for x in range(100, size, 100):
        for y in range(100, size, 100):
            dwg.add(dwg.text(
                f"({x},{y})",
                insert=(x+3, y-3),
                font_size="12",
                fill="gray"
            ))

    dwg.add(dwg.rect(insert=(0, 0), size=(size, size), fill="none", stroke="black", stroke_width=2))

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


if __name__ == "__main__":
    letter = 'B'
    large = True
    filename = f"output/letter_{letter}_{'large' if large else 'small'}.svg"
    generate_letter_svg(letter, filename, large=large)
    letter = 'B'
    large = False
    filename = f"output/letter_{letter}_{'large' if large else 'small'}.svg"
    generate_letter_svg(letter, filename, large=large)
