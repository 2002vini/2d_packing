from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors


page_width, page_height = A4
WIDTH = 0.7 * page_width
X = (page_width - WIDTH) / 2
c = canvas.Canvas("/home/vaibhav/test.pdf", pagesize=A4, bottomup=0)
margin_between_container_and_heading = 0.4 * cm
cutting_blade_margin_5mm = 5 / 25.4     # considering 1 point == 1


def draw_heading_container(data):
    heading_height = 0.155 * page_height
    heading_y_position = 30
    c.rect(X, heading_y_position, WIDTH, heading_height, stroke=1, fill=0)
    text_x = X + 0.5 * cm
    text_y = heading_y_position + 0.7 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(text_x, text_y, "Quartz Kitchen")
    heading_stats = [
        ("Total area used:", f"{data['total_area_used']} sq. ft."),
        ("Total area wasted:", f"{data['total_area_wasted']} sq. ft."),
        ("Total area of single slab:", f"{data['total_area_of_single_slab']} sq. ft."),
        ("Total area used (%):", f"{data['total_area_used_percent']}%"),
        ("Total area wasted (%):", f"{data['total_area_wasted_percent']}%"),
        ("Total no of slabs used:", f"{data['total_no_of_slabs_used']}"),
        ("Slab Size:", f"{data['slab_width']} x {data['slab_height']}"),
    ]

    c.setFont("Helvetica", 10)
    column_gap = 7 * cm
    for i, (label, value) in enumerate(heading_stats):
        c.drawString(text_x, text_y + 14 * (i + 1), label)
        c.drawString(text_x + column_gap, text_y + 14 * (i + 1), value)

    return heading_height, heading_y_position


def draw_stats_container(main_container_y_position, main_container_height, data):
    stats_rect_height = 0.115 * page_height
    stats_y_position = main_container_y_position + main_container_height
    c.rect(X, stats_y_position, WIDTH, stats_rect_height, stroke=1, fill=0)

    stat_text_x = X + 0.5 * cm
    stat_text_y = stats_y_position + 0.6 * cm

    stats_data = [
        ("Layout Number", f"{data['layout_number']} of 12"),
        ("Area occupied", f"{data['area_occupied']} sq. ft."),
        ("Area occupied (%)", f"{data['area_occupied_percent']}%"),
        ("Area wasted", f"{data['area_wasted']} sq. ft."),
        ("Area wasted (%)", f"{data['area_wasted_percent']}%"),
        ("Layout Count", f"{data['layout_count']}")
    ]

    c.setFont("Helvetica", 10)
    column_gap = 7 * cm
    for i, (label, value) in enumerate(stats_data):
        c.drawString(stat_text_x, stat_text_y + 14*i, label)
        c.drawString(stat_text_x + column_gap, stat_text_y + 14*i, value)


def draw_main_container(heading_y, heading_h, rectangles, container_width=138, container_height=78):
    container_h = 0.4 * page_height
    container_y = heading_y + heading_h + margin_between_container_and_heading

    scale_width = WIDTH / container_width
    scale_height = container_h / container_height

    c.setFillColor(colors.lightblue)
    # Draw scaled rectangles inside the main container
    for rect in rectangles:
        scaled_width = rect['width'] * scale_width
        scaled_height = rect['height'] * scale_height
        scaled_x = X + rect['x'] * scale_width
        # scaled_y = container_y + rect['y'] * scale_height
        scaled_y = container_y + container_h - (rect['y'] * scale_height + scaled_height)
        c.rect(scaled_x, scaled_y, scaled_width, scaled_height, stroke=1, fill=1)

    c.setFillColor(colors.black)
    c.rect(X, container_y, WIDTH, container_h, stroke=1, fill=0)
    return container_y, container_h


if __name__ == "__main__":
    heading_data = {
        'total_area_used': 3984.09,
        'total_area_wasted': 664.79,
        'total_area_of_single_slab': 4648.88,
        'total_area_used_percent': 85.70,
        'total_area_wasted_percent': 14.30,
        'total_no_of_slabs_used': 4,
        'slab_width': 138,
        'slab_height': 78
    }
    stats_data = {
        'layout_number': 1,
        'area_occupied': 3984.09,
        'area_wasted': 664.79,
        'layout_count': 4,
        'area_occupied_percent': 85.70,
        'area_wasted_percent': 14.30
    }
    rectangles = [
        {'width': 4.0, 'height': 36.625, 'x': 124.75, 'y': 0},
        {'width': 4.0, 'height': 36.625, 'x': 128.75, 'y': 0},
        {'width': 4.0, 'height': 36.625, 'x': 132.75, 'y': 0},
        {'width': 36.0, 'height': 25.0, 'x': 102.0, 'y': 42.0},
        {'width': 102.0, 'height': 25.0, 'x': 0, 'y': 42.0},
        {'width': 124.75, 'height': 42.0, 'x': 0, 'y': 0},
    ]

    heading_h, heading_y = draw_heading_container(heading_data)
    container_y, container_h = draw_main_container(heading_y, heading_h, rectangles)
    draw_stats_container(container_y, container_h, stats_data)

c.save()


