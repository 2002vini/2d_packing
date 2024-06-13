from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
import cmath


page_width, page_height = A4
WIDTH = 0.7 * page_width
X = (page_width - WIDTH) / 2
margin_between_container_and_heading = 1 * cm
cutting_blade_margin_5mm = 5 / 25.4     # considering 1 point == 1 inch


def draw_heading_container(c, data):
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

import cmath

def solve_quadratic(a, b, c):
    # Calculate the discriminant
    discriminant = b**2 - 4*a*c
    
    # Calculate the two solutions using cmath to handle potential complex numbers
    root1 = (-b - cmath.sqrt(discriminant)) / (2 * a)
    root2 = (-b + cmath.sqrt(discriminant)) / (2 * a)

    # Check if roots are real and return the non-negative or least negative root
    if root1.imag == 0 and root2.imag == 0:  # Checks if both roots are real numbers
        # Select the non-negative root or the root closer to zero if both are negative
        if root1.real >= 0 and root2.real >= 0:
            return min(root1.real, root2.real, key=abs)
        elif root1.real >= 0:
            return root1.real
        elif root2.real >= 0:
            return root2.real
        else:
            return min(root1.real, root2.real, key=abs)  # Both are negative, return the least negative
    elif root1.imag == 0:  # Only root1 is real
        return root1.real if root1.real >= 0 else None
    elif root2.imag == 0:  # Only root2 is real
        return root2.real if root2.real >= 0 else None
    return None  # No real roots

def draw_main_container(c, heading_y, heading_h, rectangles, container_width=138, container_height=78):
    container_h = 0.3 * page_height
    container_y = heading_y + heading_h + margin_between_container_and_heading

    scale_width = WIDTH / container_width
    scale_height = container_h / container_height
   

    for rect in rectangles:
        scaled_width = rect['width'] * scale_width
        scaled_height = rect['height'] * scale_height
        scaled_innerWidth = rect['innerWidth'] * scale_width
        scaled_innerHeight=rect['innerHeight'] * scale_height
        total_inner_area=scaled_innerHeight * scaled_innerWidth
        L_Shape_Area=(scaled_width * scaled_height) - total_inner_area
        scaled_thickness=solve_quadratic(1,-1*(scaled_width+scaled_height),L_Shape_Area)
        scaled_thickness_length=rect['thickness']*scale_height
        scaled_thickness_width=rect['thickness']*scale_width
        print("scaled_thickness is:",scaled_thickness)
        print("scaled_innerWidth is:",scaled_innerWidth)
        print("scaled_innerHeight is:",scaled_innerHeight)
        print("total_inner_area is:",total_inner_area)
        print("scaled_width is:",scaled_width)
        print("scaled_height is:",scaled_height)
        print("L_Shape_Area is:",L_Shape_Area)
        scaled_x = X + rect['x'] * scale_width
        scaled_y = container_y + container_h - (rect['y'] * scale_height + scaled_height)
        print("coordinates:",scaled_x,scaled_y,scaled_x+scaled_thickness,scaled_y+scaled_thickness)
     
        c.setFillColor(colors.lightblue if scaled_thickness == 0 else colors.transparent)
        c.rect(scaled_x, scaled_y, scaled_width, scaled_height, stroke=1, fill=1)
        if scaled_thickness > 0 and scaled_innerWidth==0.0 and scaled_innerHeight==0.0:
            c.setFillColor(colors.darkblue)
            c.rect(scaled_x, scaled_y, scaled_thickness_length, scaled_height, stroke=0, fill=1)
            c.rect(scaled_x, scaled_y, scaled_width, scaled_thickness_width, stroke=0, fill=1)
        elif scaled_innerWidth > 0 and scaled_innerHeight > 0:
            print("complex shape")
            # Draw inscribed L-shape
            c.setFillColor(colors.darkblue)
            c.rect(scaled_x, scaled_y, scaled_thickness_width, scaled_height, stroke=0, fill=1)
            c.rect(scaled_x, scaled_y, scaled_width, scaled_thickness_length, stroke=0, fill=1)
            
            # Draw inner rectangle
            c.setFillColor(colors.lightgreen)
            # inner_scaled_x = scaled_x + scaled_thickness * scale_width
            # inner_scaled_y = scaled_y + scaled_thickness * scale_height
            # inner_scaled_width = scaled_innerWidth * scale_width
            # inner_scaled_height = scaled_innerHeight * scale_height
            # c.rect(inner_scaled_x, inner_scaled_y, inner_scaled_width, inner_scaled_height, stroke=1, fill=1)
            c.rect(scaled_x+scaled_thickness_width, scaled_y+scaled_thickness_length, scaled_innerWidth, scaled_innerHeight, stroke=1, fill=1)


        # Determine text orientation based on rectangle dimensions
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 5)
        rect_actual_width = rect['width'] - cutting_blade_margin_5mm
        rect_actual_height = rect['height'] - cutting_blade_margin_5mm
        

        code_text = f"Code: {rect['code']}"
        size_text = f"Size: {rect_actual_width} x {rect_actual_height}"
        # Calculate center positions
        center_x = scaled_x + scaled_width / 2
        center_y = scaled_y + scaled_height / 2   

        

        if rect['width'] < rect['height']:
            # Rotate text for vertical rectangles
            c.saveState()
            c.translate(scaled_x + scaled_width / 2, scaled_y + scaled_height / 2)
            c.rotate(90)
            c.drawCentredString(0, -1, code_text)  # Shift text slightly
            c.drawCentredString(0, 5, size_text)
            c.restoreState()
        else:
            c.drawCentredString(center_x, center_y - 3, code_text)
            c.drawCentredString(center_x, center_y + 3, size_text)

    c.setFillColor(colors.black)
    c.rect(X, container_y, WIDTH, container_h, stroke=1, fill=0)
    return container_y, container_h


def draw_stats_container(c, main_container_y_position, main_container_height, data):
    stats_rect_height = 0.13 * page_height
    stats_y_position = main_container_y_position + main_container_height
    c.rect(X, stats_y_position, WIDTH, stats_rect_height, stroke=1, fill=0)

    stat_text_x = X + 0.5 * cm
    stat_text_y = stats_y_position + 0.6 * cm

    stats_data = [
        ("Layout Number", f"{data['layout_number']} of {data['unique_layouts_count']}"),
        ("Area occupied", f"{data['area_occupied']} sq. ft."),
        ("Area occupied (%)", f"{data['area_occupied_percent']}%"),
        ("Area wasted", f"{data['area_wasted']} sq. ft."),
        ("Area wasted (%)", f"{data['area_wasted_percent']}%"),
        ("Layout Count", f"{data['layout_count']}"),
        ("Total RFT", f"{data['total_rft']}"),
    ]

    c.setFont("Helvetica", 10)
    column_gap = 7 * cm
    for i, (label, value) in enumerate(stats_data):
        c.drawString(stat_text_x, stat_text_y + 14*i, label)
        c.drawString(stat_text_x + column_gap, stat_text_y + 14*i, value)

