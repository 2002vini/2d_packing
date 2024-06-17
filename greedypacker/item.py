"""
2D Item class.
"""
class Item:
    """
    Items class for rectangles inserted into sheets
    """
    def __init__(self, width, height,
                 CornerPoint: tuple = (0, 0),
                 rotation: bool = True) -> None:
        self.width = width
        self.height = height
        self.x = CornerPoint[0]
        self.y = CornerPoint[1]
        self.area = self.width * self.height
        self.rotated = False
        self.id = 0


    def __repr__(self):
        return 'Item(width=%r, height=%r, x=%r, y=%r)' % (self.width, self.height, self.x, self.y)


    def rotate(self) -> None:
        self.width, self.height = self.height, self.width
        self.rotated = False if self.rotated == True else True


class CustomItem(Item):
    def __init__(self, width: float, height: float, code, polish_edge_l, polish_edge_w, thickness: float = 0.0, child_items=None, CornerPoint=(0, 0), rotation=True):
        super().__init__(width, height, CornerPoint, rotation)
        self.code = code
        self.polish_edge_l = polish_edge_l
        self.polish_edge_w = polish_edge_w
        self.thickness = thickness
        # Initialize child_items as an empty list if None is provided
        self.child_items = child_items if child_items is not None else []

    def __repr__(self):
        return (f'CustomItem(width={self.width!r}, height={self.height!r}, x={self.x!r}, y={self.y!r}, '
                f'thickness={self.thickness!r}, '
                f'code={self.code!r}, polish_edge_l={self.polish_edge_l!r}, polish_edge_w={self.polish_edge_w!r}, '
                f'child_items={self.child_items})')

    def rotate(self):
        super().rotate()
        # Rotate all child items
        for child in self.child_items:
            child.rotate()

    def add_child(self, child):
        """Adds a new CustomItem to the child_items list."""
        if isinstance(child, CustomItem):
            self.child_items.append(child)
        else:
            raise ValueError("child must be an instance of CustomItem")

    def remove_child(self, child):
        """Removes a CustomItem from the child_items list."""
        try:
            self.child_items.remove(child)
        except ValueError:
            print("Item not found in the child list")

