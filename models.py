class Node:
    def __init__(self, node_type=None, left=None, right=None, value=None):
        self.type = node_type
        self.left = left
        self.right = right
        self.value = value

    def __repr__(self):
        return f"Node({self.type}, {self.left}, {self.right}, {self.value})"

    def to_dict(self):
        return {
            "type": self.type,
            "left": self.left.to_dict() if isinstance(self.left, Node) else self.left,
            "right": self.right.to_dict() if isinstance(self.right, Node) else self.right,
            "value": self.value.to_dict() if isinstance(self.value, Node) else self.value
        }
