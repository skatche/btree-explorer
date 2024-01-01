from tkinter import *
from tkinter import ttk

from btree import BTree


class NodeItem:
    TAG = "node"
    RADIUS = 10
    SELECT_RADIUS = RADIUS + 6
    FILL_COLOR = "white"
    OUTLINE_COLOR = "black"
    OUTLINE_WIDTH = 2
    LABEL_COLOR = "black"

    def __init__(self, canvas, coords, text=""):
        self.canvas = canvas
        self.coords = coords
        self.text = text
        self.on_mouse1 = None
        self.on_mouse2 = None

        self.items = object()

        x, y = coords

        self.item_highlight_circle = self.canvas.create_oval(
            x - NodeItem.SELECT_RADIUS, y - NodeItem.SELECT_RADIUS,
            x + NodeItem.SELECT_RADIUS, y + NodeItem.SELECT_RADIUS,
            outline=NodeItem.OUTLINE_COLOR,
            width=NodeItem.OUTLINE_WIDTH,
            state=HIDDEN,
            tags=[NodeItem.TAG]
        )

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

        def mouse_in(evt):
            self.canvas.itemconfig(self.item_highlight_circle, state=NORMAL)

        def mouse_out(evt):
            self.canvas.itemconfig(self.item_highlight_circle, state=HIDDEN)
        
        self.canvas.tag_bind(self.item_main_circle, "<Enter>", mouse_in)
        self.canvas.tag_bind(self.item_label, "<Enter>", mouse_in)
        self.canvas.tag_bind(self.item_main_circle, "<Leave>", mouse_out)
    
    def bind_mouse1(self, callback):
        self.on_mouse1 = callback
        self.canvas.tag_bind(self.item_main_circle, "<Button-1>", self.on_mouse1)
        self.canvas.tag_bind(self.item_label, "<Button-1>", self.on_mouse1)
    
    def unbind_mouse1(self):
        self.canvas.tag_bind(self.item_main_circle, "<Button-1>", None)
        self.canvas.tag_bind(self.item_label, "<Button-1>", None)
    
    def bind_mouse2(self, callback):
        self.on_mouse2 = callback
        # Tk inexplicably uses Button-2 for the middle mouse button and Button-3 for the right mouse button
        self.canvas.tag_bind(self.item_main_circle, "<Button-3>", self.on_mouse2)
        self.canvas.tag_bind(self.item_label, "<Button-3>", self.on_mouse2)
    
    def unbind_mouse2(self):
        self.canvas.tag_bind(self.item_main_circle, "<Button-3>", None)
        self.canvas.tag_bind(self.item_label, "<Button-3>", None)
    
    def set_text(self, text):
        self.canvas.itemconfigure(self.item_label, text=text)
    
    def move_to(self, coords, update=False):
        self.coords = coords
        self._update_items()
        
        if update:
            self.canvas.update()
    
    def _update_items(self):
        self._update_highlight_circle()
        self._update_main_circle()
        self._update_label()
    
    def _update_main_circle(self):
        x, y = self.coords
        x1, y1 = x - NodeItem.RADIUS, y - NodeItem.RADIUS
        x2, y2 = x + NodeItem.RADIUS, y + NodeItem.RADIUS
        self.canvas.coords(self.item_main_circle, x1, y1, x2, y2)
    
    def _update_highlight_circle(self):
        # We need to hide the highlight circle, otherwise it might remain visible after moving away from the mouse cursor
        self.canvas.itemconfigure(self.item_highlight_circle, state=HIDDEN)
        x, y = self.coords
        x1, y1 = x - NodeItem.SELECT_RADIUS, y - NodeItem.SELECT_RADIUS,
        x2, y2 = x + NodeItem.SELECT_RADIUS, y + NodeItem.SELECT_RADIUS
        self.canvas.coords(self.item_highlight_circle, x1, y1, x2, y2)
    
    def _update_label(self):
        x, y = self.coords
        self.canvas.coords(self.item_label, x, y)
        self.canvas.itemconfig(self.item_label, text=self.text)
    
    def delete(self):
        self.canvas.delete(self.item_highlight_circle)
        self.canvas.delete(self.item_main_circle)
        self.canvas.delete(self.item_label)
    
    # def __del__(self):
    #     self.delete()

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
    
    # def __del__(self):
    #     self.delete()

# It's tempting to inherit from Canvas, but I'd rather avoid name conflicts etc.
# Instead we inherit from BTree and store the canvas as an attribute.
class BTreeCanvas(BTree):
    HORIZ_SPACING = 40
    VERT_SPACING = 40
    TOP_PADDING = 40

    def __init__(self, canvas, vals=None):
        super().__init__(vals)

        self.canvas = canvas
        self.node_items = {} # dict : BTNode -> NodeItem
        self.connection_items = {} # dict : BTNode -> ConnectionItem | None,
                                   # connecting the node with its parent (or None if root)
        self.guideline_items = {} # dict: BTNode -> id of line item in canvas

        if vals is not None:
            self.build_items()
    
    def insert(self, val):
        new_node = super().insert(val)
        self.build_items()

        return new_node
    
    def delete_node(self, node):
        # if self.node_items.get(node, None) is not None:
        self.node_items[node].delete()
        del self.node_items[node]
        
        if self.connection_items.get(node, None) is not None:
            self.connection_items[node].delete()
            del self.connection_items[node]
        
        super().delete_node(node)
        
        self.build_items()

    def rotate_pivot(self, pivot):
        super().rotate_pivot(pivot)
        self.build_items()
    
    def build_items(self):
        if self.root is None:
            return

        nodes = self.sorted_nodes()
        coords = self.build_inorder_coords(nodes)
        
        # create/update NodeItems
        for i in range(len(nodes)):
            if nodes[i] in self.node_items:
                self.node_items[nodes[i]].move_to(coords[i])
            else:
                self.node_items[nodes[i]] = self.build_node_item(nodes[i], coords[i])
            
        # create/update ConnectionItems to parents
        for i in range(len(nodes)):
            if nodes[i].parent is None:
                if self.connection_items.get(nodes[i], None) is not None:
                    self.connection_items[nodes[i]].delete()
                self.connection_items[nodes[i]] = None
            else:
                if self.connection_items.get(nodes[i], None) is not None:
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
    
    def build_inorder_coords(self, nodes):
        canvas_config = self.canvas.config()
        width, height = int(canvas_config["width"][-1]), int(canvas_config["height"][-1])
        midpoint = width // 2

        root_index = nodes.index(self.root)

        # keep the root node centred, evenly space the nodes on either side
        x_coords = [midpoint + (i - root_index) * BTreeCanvas.HORIZ_SPACING for i in range(len(nodes))]

        # the nodes are in order horizontally, and lowered vertically based on their depth
        depths = map(self.depth_of_node, nodes)
        y_coords = [BTreeCanvas.TOP_PADDING + d * BTreeCanvas.VERT_SPACING for d in depths]

        return list(zip(x_coords, y_coords))

    def build_node_item(self, node, coords):
        node_item = NodeItem(self.canvas, coords, text=str(node.val))
        
        def mouse1_callback(evt):
            self.rotate_pivot(node)
        node_item.bind_mouse1(mouse1_callback)

        def mouse2_callback(evt):
            self.delete_node(node)
        node_item.bind_mouse2(mouse2_callback)

        return node_item