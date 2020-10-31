import re

class RegexTreeNode():
    def __init__(self, regex, children):
        self.regex = re.compile("^" + regex + "$")
        self.display_name = regex
        self.children = children

    def match_update(self, field):
        if self.regex.fullmatch(field) is None:
            return False
        self.children = [node for node in self.children if node.match_update(field)]
        return True

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

    def extract_pattern(self, policy = ""):
        if self.nullable:
            return "(" + self.root.extract_pattern(policy) + ")?"
        return self.root.extract_pattern(policy)

    def make_nullable(self):
        self.nullable = True
