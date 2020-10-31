import re

class RegexTreeNode():
    def __init__(self, regex, children):
        self.regex = re.compile("^" + regex + "$")
        self.display_name = regex
        self.children = children

    def match_update(self, field):
        if self.regex.fullmatch(field) is None:
            return False, True
        new_children = []
        has_dropped_node = False
        for node in self.children:
            match, has_dropped = node.match_update(field)
            if match:
                new_children.append(node)
            if has_dropped:
                has_dropped_node = True
        self.children = new_children
        return True, has_dropped_node

    def extract_pattern(self, policy):
        if policy == "first_leaf":
            return self.get_first_leaf()
        return self.get_first_intersect_or_leaf()

    def get_first_intersect_or_leaf(self):
        if len(self.children) != 1:
            return self.display_name
        return self.children[0].get_first_intersect_or_leaf()

    def get_first_leaf(self):
        if len(self.children) > 0:
            return self.children[0].get_first_leaf()
        return self.display_name

    def match_to_leaf(self, field):
        if self.regex.fullmatch(field) is None:
            return False
        if len(self.children) == 0:
            return True
        for child in self.children:
            if child.match_to_leaf(field):
                return True
        return False

    def merge_tree(self, node):
        new_children = []
        for selfChild in self.children:
            for otherChild in node.children:
                if selfChild.regex == otherChild.regex:
                    selfChild.merge_tree(otherChild)
                    new_children.append(selfChild)
        self.children = new_children
        # FIXME: Requires optimization


class RegexTree():
    def __init__(self):
        self.root = RegexTreeNode(".*", [
            RegexTreeNode("\d*", []),
            RegexTreeNode("\[.*\]", [
                RegexTreeNode("\[(DEBUG|INFO|WARN|ERROR)\]", [])
            ])
        ])
        # Is actually CONSTANT
        self.initialized = False
        # Is actually the REPR
        self.first_value = None
        # has been compared to a GAP
        self.nullable = False

    def merge_pattern(self, field):
        """The root node must ALWAYS MATCH the field"""
        if field is None:
            return
        if isinstance(field, RegexTree):
            self.merge_tree(field)
            return
        if not self.initialized:
            if self.first_value is None:
                self.first_value = field
                self.root.match_update(self.first_value)
                return
            if self.first_value == field:
                return
            self.initialized = True
        _, has_dropped = self.root.match_update(field)
        if has_dropped:
            self.first_value = field

    def merge_tree(self, tree):
        if not tree.initialized:
            self.merge_pattern(tree.first_value)
            return
        if not self.initialized and tree.initialized:
            tree.merge_pattern(self.first_value)
            self.root = tree.root
            self.first_value = tree.first_value
            self.nullable = tree.nullable or self.nullable
            self.initialized = tree.initialized
            return
        self.root.merge_tree(tree.root)
        self.nullable = tree.nullable or self.nullable

    def extract_pattern(self, policy="first_leaf"):
        if self.nullable:
            return "(" + self.root.extract_pattern(policy) + ")?"
        return self.root.extract_pattern(policy)

    def make_nullable(self):
        self.nullable = True

    def get_repr(self, reprB):
        if not self.initialized:
            return self.first_value
        if len(self.root.children) == 0:
            return self.first_value
        if self.root.match_to_leaf(reprB):
            return reprB
        return self.first_value

    def __eq__(self, obj):
        # FIXME: current is a match to **ANY** leaf
        if isinstance(obj, str):
            return self.root.match_to_leaf(obj)
        # Trick to compare trees is to try to match their repr
        if (self.root.match_to_leaf(obj.first_value) and
            obj.root.match_to_leaf(self.first_value)):
            return True
        return False
