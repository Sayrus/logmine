from .vendor.alignment import water
from .regex_tree import RegexTree


class PatternPlaceholder(str):
    pass


class PatternGenerator():
    def __init__(self, placeholder='---'):
        self.placeholder = placeholder

    # FIXME: Handle tree
    def create_pattern(self, a, b):
        if len(a) == 0 and len(b) == 0:
            return []
        (a, b) = water(a, b)
        new = []
        for i in range(len(a)):
            if a[i] == "-":
                tree = RegexTree()
                tree.merge_pattern(b[i])
                new.append(tree)
            elif b[i] == "-":
                a[i].make_nullable()
                new.append(a[i])
            else:
                a[i].merge_pattern(b[i])
                new.append(a[i])
        return new
