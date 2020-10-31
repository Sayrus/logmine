import re

class RegexTreeNode():
    def __init__(self, regex, children):
        self.regex = re.compile(regex)
        self.children = children

    def match_update(self, field):
        if self.regex.fullmatch(field) is None:
            return False
        self.children = [node for node in self.children if node.match_update(field)]
        return True

    def get_first_leaf(self):
        if len(self.children) > 0:
            return self.children[0].get_first_leaf()
        return self.regex.pattern

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
        self.initialized = False
        self.first_value = None
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
                return
            if self.first_value == field:
                return
            self.initialized = True
            self.root.match_update(self.first_value)
        self.root.match_update(field)

    def merge_tree(self, tree):
        if self.initialized == False and tree.initialized == False:
            # If value has yet to be provided
            if self.first_value is None and tree.first_value is None:
                return
            # If only the first tree has a value
            if tree.first_value is None:
                return
            # If only the second tree has a value
            if self.first_value is None:
                self.root = tree.root
                self.first_value = tree.first_value
                self.nullable = tree.nullable or self.nullable
                return
            # If both have a value
            self.merge_pattern(tree.first_value)
            return
        if self.initialized == False and tree.initialized == True:
            tree.merge_pattern(self.first_value)
            self.root = tree.root
            self.first_value = tree.first_value
            self.nullable = tree.nullable or self.nullable
            self.initialized = tree.initialized
            return
        if self.initialized == True and tree.initialized == False:
            self.merge_pattern(tree.first_value)
            return
        self.root.merge_tree(tree.root)
        self.nullable = tree.nullable or self.nullable

    def extract_pattern(self):
        """To avoid heuristics, we return the first leaf."""
        # FIXME: Add heuristics
        # Not initialized means constant
        return self.root.get_first_leaf()

    def __repr__(self):
        return "REPR"
        return self.extract_pattern()

    def __str__(self):
        return "STR"
        return self.extract_pattern()

    def make_nullable(self):
        self.nullable = True

    def __eq__(self, obj):
        # FIXME: current is a match to **ANY** leaf
        # Trick as we only compare to string
        if not isinstance(obj, str):
            return False
        self.root.match_to_leaf(obj)
