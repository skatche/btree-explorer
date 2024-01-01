class Foo:
    def __init__(self, val):
        self.val = val
    
    def __repr__(self):
        return f"Foo({self.val})"

L = [Foo(n) for n in range(10)]

F = []
for k in range(len(L)):
    def foo():
        print (L[k].val)
    F.append(foo)

for k in range(len(F)):
    F[k]()