import time
import random
from tkinter import *
from tkinter import ttk

from btreecanvas import *

root = Tk()
root.title("BTree Explorer")

mainframe = ttk.Frame(root)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

canvas = Canvas(mainframe, width=1024, height=768, background="gray75")
canvas.pack()

btree_canvas = BTreeCanvas(canvas)
vals = list(range(10))
random.shuffle(vals)

for v in vals:
    btree_canvas.insert(v)

root.mainloop()