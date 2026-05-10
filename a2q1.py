class End:
    def __init__(self, val=0):
        self.val = val

class Node:
    def __init__(self, start, end, suffix_link = None, isLeaf = False, isRoot = False):
        self.start: int = start
        self.end: int | End = end
        self.suffix_link: Node = suffix_link
        self.children = [None for _ in range(126-36+1)]
        self.isLeaf: bool = isLeaf
        self.isRoot: bool = isRoot

class Ukkonen_algorithm:
    def __init__(self):
        self.root = Node(-1, -1, isLeaf = False, isRoot= True)
        self.root.suffix_link = self.root 
        self.ALPHABET_START = 36
        self.ALPHABET_END = 126
        self.global_end = End(0)
        self.active_node: Node = self.root
        self.remainder: tuple[int, int] = None
        self.pending_node: Node = None # When a new node is created in extension j it's suffix link 
                                      # will be resolved in extension j+1

    def construct_suffix_array(self, txt):
        txt_with_dollar = txt + '$'
        phase_i = 0
        extension_j = 0
        while phase_i >= len(txt_with_dollar):
            while extension_j <= phase_i:
                return
            
    def rule_two_regular(self, active_node: Node, remainder: tuple[int, int], txt_with_dollar, phase_i, new_remainder):
        remainder_start, remainder_end = remainder
        remainder_length = remainder_end - remainder_start + 1

        # the edge we are splitting: find the child of active_node that remainder starts with
        first_char_index = ord(txt_with_dollar[remainder_start]) - self.ALPHABET_START
        edge_node = active_node.children[first_char_index]

        split_end = edge_node.start + remainder_length - 1
        new_internal_node = self.create_new_internal_node(edge_node.start, split_end)

        # Attach the edge node to the internal node instead
        index_after_split_end = split_end + 1
        edge_node.start = index_after_split_end
        start_index_char = ord(txt_with_dollar[index_after_split_end]) - self.ALPHABET_START
        new_internal_node.children[start_index_char] = edge_node

        # Now we'll create a new leaf node for the phase_i character that caused rule 2 regular
        # to occur in the first place and attach it to the newly created internal node
        new_leaf_for_phase_i = self.create_new_leaf(phase_i)
        start_index_char = ord(txt_with_dollar[phase_i]) - self.ALPHABET_START
        new_internal_node.children[start_index_char] = new_leaf_for_phase_i

        # Connect the new internal node to the active node
        active_node.children[first_char_index] = new_internal_node

        # If the previous extension's pending node hasn't been resolved yet then the pending
        # node will form a sufffix link to the newly created internal node
        if self.pending_node is not None:
            self.pending_node.suffix_link = new_internal_node
        
        # We'll set the new internal node as unresolved 
        self.pending_node = new_internal_node

        self.active_node = active_node.suffix_link
        self.remainder = new_remainder
    
    def rule_two_alternate(self, active_node: Node, start: int, txt_with_dollar, new_active_node, new_remainder):
        leaf_node = self.create_new_leaf(start)
        start_index_char = ord(txt_with_dollar[start]) - self.ALPHABET_START
        active_node.children[start_index_char] = leaf_node

        # If the previous extension's pending node hasn't been resolved yet then the active node
        # for this extension will resolve it
        if self.pending_node is not None:
            self.pending_node.suffix_link = active_node
            self.pending_node = None

        self.active_node = new_active_node
        self.remainder = new_remainder
    
    def rule_three(self, new_active_node, new_remainder):
        self.active_node = new_active_node
        self.remainder = new_remainder

    def create_new_leaf(self, start: int) -> Node:
        return Node(start, self.global_end, isLeaf=True)

    def create_new_internal_node(self, start: int, end: int) -> Node:
        return Node(start, end, isLeaf=False)
    




