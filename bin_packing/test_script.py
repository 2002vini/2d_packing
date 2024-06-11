from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib import colors


rectangles = [
    {'width': 4.0, 'height': 36.625, 'x': 124.75, 'y': 0},
    {'width': 4.0, 'height': 36.625, 'x': 128.75, 'y': 0},
    {'width': 4.0, 'height': 36.625, 'x': 132.75, 'y': 0},
    {'width': 36.0, 'height': 25.0, 'x': 102.0, 'y': 42.0},
    {'width': 102.0, 'height': 25.0, 'x': 0, 'y': 42.0},
    {'width': 124.75, 'height': 42.0, 'x': 0, 'y': 0},
]

page_width, page_height = A4
WIDTH = 0.7 * page_width
X = (page_width - WIDTH) / 2
c = canvas.Canvas("/home/vaibhav/test.pdf", pagesize=A4, bottomup=0)


def draw_heading_container():
    heading_height = 0.155 * page_height
    heading_y_position = 30
    c.rect(X, heading_y_position, WIDTH, heading_height, stroke=1, fill=0)
    text_x = X + 0.5 * cm
    text_y = heading_y_position + 0.7 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(text_x, text_y, "Quartz Kitchen")

    heading_stats = [
        ("Total area used:", "3984.09 sq. ft."),
        ("Total area wasted:", "664.79 sq. ft."),
        ("Total area of single slab:", "10626.00 sq. ft."),
        ("Total area used (%):", "85.70%"),
        ("Total area wasted (%):", "14.30%"),
        ("Total no of slabs used:", "63"),
        ("Slab Size:", "138 x 78")
    ]

    c.setFont("Helvetica", 10)
    column_gap = 7 * cm
    for i, (label, value) in enumerate(heading_stats):
        c.drawString(text_x, text_y + 14 * (i + 1), label)
        c.drawString(text_x + column_gap, text_y + 14 * (i + 1), value)

    return heading_height, heading_y_position


def draw_stats_container(main_container_y_position, main_container_height):
    stats_rect_height = 0.115 * page_height
    stats_y_position = main_container_y_position + main_container_height
    c.rect(X, stats_y_position, WIDTH, stats_rect_height, stroke=1, fill=0)

    stat_text_x = X + 0.5 * cm
    stat_text_y = stats_y_position + 0.6 * cm

    stats_data = [
        ("Layout Number", "1 of 12"),
        ("Area occupied", "3984.09 sq. ft."),
        ("Area occupied (%)", "85.70%"),
        ("Area wasted", "664.79 sq. ft."),
        ("Area wasted (%)", "14.30%"),
        ("Layout Count", "4")
    ]

    c.setFont("Helvetica", 10)
    column_gap = 7 * cm
    for i, (label, value) in enumerate(stats_data):
        c.drawString(stat_text_x, stat_text_y + 14*i, label)
        c.drawString(stat_text_x + column_gap, stat_text_y + 14*i, value)


def draw_main_container(heading_y, heading_h):
    container_h = 0.4 * page_height
    container_y = heading_y + heading_h + 0.4*cm

    original_width, original_height = 138, 78

    scale_width = WIDTH / original_width
    scale_height = container_h / original_height

    c.setFillColor(colors.lightblue)
    # Draw scaled rectangles inside the main container
    for rect in rectangles:
        scaled_width = rect['width'] * scale_width
        scaled_height = rect['height'] * scale_height
        scaled_x = X + rect['x'] * scale_width
        scaled_y = container_y + rect['y'] * scale_height
        c.rect(scaled_x, scaled_y, scaled_width, scaled_height, stroke=1, fill=1)

    c.setFillColor(colors.black)
    c.rect(X, container_y, WIDTH, container_h, stroke=1, fill=0)
    return container_y, container_h


if __name__ == "__main__":
    heading_h, heading_y = draw_heading_container()
    container_y, container_h = draw_main_container(heading_y, heading_h)
    draw_stats_container(container_y, container_h)

c.save()

