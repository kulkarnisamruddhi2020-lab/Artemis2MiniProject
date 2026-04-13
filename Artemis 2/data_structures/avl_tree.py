class AVLNode:
    def __init__(self, timestamp, telemetry):
        self.timestamp = timestamp
        self.telemetry = telemetry
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def __init__(self):
        self.root = None

    def insert(self, timestamp, telemetry):
        self.root = self._insert(self.root, timestamp, telemetry)

    def _insert(self, node, timestamp, telemetry):
        if not node:
            return AVLNode(timestamp, telemetry)
        
        if timestamp < node.timestamp:
            node.left = self._insert(node.left, timestamp, telemetry)
        elif timestamp > node.timestamp:
            node.right = self._insert(node.right, timestamp, telemetry)
        else:
            # Duplicate timestamps updated
            node.telemetry = telemetry
            return node

        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)

        # Left Left
        if balance > 1 and timestamp < node.left.timestamp:
            return self._right_rotate(node)
        
        # Right Right
        if balance < -1 and timestamp > node.right.timestamp:
            return self._left_rotate(node)
        
        # Left Right
        if balance > 1 and timestamp > node.left.timestamp:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        
        # Right Left
        if balance < -1 and timestamp < node.right.timestamp:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def search(self, timestamp):
        # Fallback to closest prior timestamp (floor) if exact doesn't exist
        return self._search_floor(self.root, timestamp, None)

    def _search_floor(self, node, timestamp, best_node):
        if not node:
            return best_node.telemetry if best_node else None
            
        if node.timestamp == timestamp:
            return node.telemetry
            
        if timestamp < node.timestamp:
            return self._search_floor(node.left, timestamp, best_node)
            
        # If timestamp > node.timestamp, this node is a candidate for closest past event
        return self._search_floor(node.right, timestamp, node)

    def _left_rotate(self, z):
        y = z.right
        T2 = y.left

        y.left = z
        z.right = T2

        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        return y

    def _right_rotate(self, z):
        y = z.left
        T3 = y.right

        y.right = z
        z.left = T3

        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        return y

    def _get_height(self, node):
        if not node:
            return 0
        return node.height

    def _get_balance(self, node):
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)
