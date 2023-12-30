from tkinter import *
from tkinter import ttk

from btree import BTree


class NodeItem:
    TAG = "node"
    RADIUS = 10
    FILL_COLOR = "white"
    OUTLINE_COLOR = "black"
    OUTLINE_WIDTH = 2
    LABEL_COLOR = "black"

    def __init__(self, canvas, coords, text=""):
        self.canvas = canvas
        self.coords = coords

        self.items = object()

        x, y = coords

        self.item_main_circle = self.canvas.create_oval(
            x - NodeItem.RADIUS, y - NodeItem.RADIUS,
            x + NodeItem.RADIUS, y + NodeItem.RADIUS,
            fill=NodeItem.FILL_COLOR,
            outline=NodeItem.OUTLINE_COLOR,
            width=NodeItem.OUTLINE_WIDTH,
            tags=[NodeItem.TAG]

        )

        self.item_label = self.canvas.create_text(
            x, y,
            text=text,
            fill=NodeItem.LABEL_COLOR,
            tags=[NodeItem.TAG]
        )
    
    def set_text(self, text):
        self.canvas.itemconfigure(self.item_label, text=text)
    
    def move_to(self, coords, update=False):
        self.coords = coords
        x, y = self.coords
        x1, y1 = x - NodeItem.RADIUS, y - NodeItem.RADIUS
        x2, y2 = x + NodeItem.RADIUS, y + NodeItem.RADIUS
        self.canvas.coords(self.item_main_circle, x1, y1, x2, y2)
        self.canvas.coords(self.item_label, x, y)
        
        if update:
            self.canvas.update()
    
    def lift(self):
        self.canvas.tag_raise(self.item_main_circle)
        self.canvas.tag_raise(self.item_label)
    
    def delete(self):
        self.canvas.delete(self.item_main_circle)
        self.canvas.delete(self.item_label)
    
    def __del__(self):
        self.delete()

class ConnectionItem:
    TAG = "connection"
    LINE_COLOR = "black"

    def __init__(self, canvas, node_item1, node_item2):
        self.canvas = canvas
        self.node_item1 = node_item1
        self.node_item2 = node_item2

        coords1 = self.node_item1.coords
        coords2 = self.node_item2.coords

        self.item_line = self.canvas.create_line(
            (coords1, coords2),
            fill=ConnectionItem.LINE_COLOR,
            tags=[ConnectionItem.TAG]
        )
    
    def set_node1(self, node):
        self.node_item1 = node
        self.update_coords()
    
    def set_node2(self, node):
        self.node_item2 = node
        self.update_coords()
    
    def set_nodes(self, node1, node2):
        self.node_item1 = node1
        self.node_item2 = node2
        self.update_coords()
    
    def update_coords(self, update=False):
        coords1 = self.node_item1.coords
        coords2 = self.node_item2.coords

        self.move_to(coords1 + coords2, update)

    def move_to(self, coords, update=False):
        self.canvas.coords(self.item_line, *coords)
        
        if update:
            self.canvas.update()
    
    def delete(self):
        self.canvas.delete(self.item_line)
    
    def __del__(self):
        self.delete()

# It's tempting to inherit from Canvas, but I'd rather avoid name conflicts etc.
# Instead we inherit from BTree and store the canvas as an attribute.
class BTreeCanvas(BTree):
    HORIZ_SPACING = 40
    VERT_SPACING = 40
    TOP_PADDING = 40

    def __init__(self, canvas):
        super().__init__()

        self.canvas = canvas
        self.node_items = {} # dict : BTNode -> NodeItem
        self.connection_items = {} # dict : BTNode -> ConnectionItem | None,
                                   # connecting the node with its parent (or None if root)
    
    def insert(self, val):
        new_node = super().insert(val)
        self.build_items()

        return new_node
    
    def build_items(self):
        if self.root is None:
            return
        
        canvas_config = self.canvas.config()
        width, height = int(canvas_config["width"][-1]), int(canvas_config["height"][-1])
        midpoint = width // 2

        nodes = self.sorted_nodes()
        root_index = nodes.index(self.root)

        # keep the root node centred, evenly space the nodes on either side
        x_coords = [midpoint + (i - root_index) * BTreeCanvas.HORIZ_SPACING for i in range(len(nodes))]

        # the nodes are in order horizontally, and lowered vertically based on their depth
        depths = map(self.depth_of_node, nodes)
        y_coords = [BTreeCanvas.TOP_PADDING + d * BTreeCanvas.VERT_SPACING for d in depths]

        coords = list(zip(x_coords, y_coords))
        
        # create/update NodeItems
        for i in range(len(nodes)):
            if nodes[i] in self.node_items:
                self.node_items[nodes[i]].move_to(coords[i])
            else:
                self.node_items[nodes[i]] = NodeItem(self.canvas, coords[i], text=str(nodes[i].val))
            
        # create/update ConnectionItems to parents
        for i in range(len(nodes)):
            if nodes[i].parent is None:
                if self.connection_items.get(nodes[i], None) is not None:
                    self.connection_items[nodes[i]].delete()
                self.connection_items[nodes[i]] = None
            else:
                if nodes[i] in self.connection_items:
                    self.connection_items[nodes[i]].set_nodes(
                        self.node_items[nodes[i].parent],
                        self.node_items[nodes[i]]
                    )
                else:
                    self.connection_items[nodes[i]] = ConnectionItem(
                        self.canvas, 
                        self.node_items[nodes[i].parent],
                        self.node_items[nodes[i]]
                    )
        
        self.canvas.tag_raise(NodeItem.TAG)
        self.canvas.update()