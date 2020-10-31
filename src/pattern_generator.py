from .vendor.alignment import water
from .regex_tree import RegexTree


class PatternPlaceholder(str):
    pass


class PatternGenerator():
    def __init__(self, placeholder='---'):
        self.placeholder = placeholder

    # FIXME: Handle tree
    def create_pattern(self, a, b, reprA = None, reprB = None):
        if len(a) == 0 and len(b) == 0:
            return []
        if reprA is None:
            reprA = a
        if reprB is None:
            reprB = b
        (w_a, w_b) = water(reprA, reprB)
        new = []
        offsetA = 0
        offsetB = 0
        for i in range(len(w_a)):
            if w_a[i] is None:
                offsetA += 1
                tree = RegexTree()
                tree.merge_pattern(b[i - offsetB])
                new.append(tree)
            elif w_b[i] is None:
                offsetB += 1
                a[i - offsetA].make_nullable()
                new.append(a[i - offsetA])
            else:
                a[i - offsetA].merge_pattern(b[i - offsetB])
                new.append(a[i - offsetA])
        return new
