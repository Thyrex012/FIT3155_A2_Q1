# Ekrithyreach Lay
# Student ID: 33698759

#################################################################
# Data structure to support the construction of the suffix tree
#################################################################
class End:
    def __init__(self, val=0):
        self.val = val

class Node:
    def __init__(self, suffix_link = None, isLeaf = False, isRoot = False, suffix_index = -1):
        self.suffix_link: Node = suffix_link
        self.children = [None for _ in range(126-36+1)]
        self.isLeaf = isLeaf
        self.isRoot = isRoot
        self.suffix_index = suffix_index

class Edge:
    def __init__(self, start: int, end: int | End, child_node: Node):
        self.start = start
        self.end = end
        self.child_node = child_node
    
    def get_end_val(self):
        if isinstance(self.end, End):
            return self.end.val
        else:
            return self.end
    
    def get_length(self):
        return self.get_end_val() - self.start + 1

#########################
#  Ukkonen's algorithm
#########################
class Ukkonen_algorithm:
    def __init__(self):
        self.root = Node(isLeaf = False, isRoot= True)
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
        n = len(txt_with_dollar)
        last_j = 0
        for i in range(n):
            self.global_end.val = i
            for j in range(last_j, i+1):
                self.active_node, self.remainder = self.traverse(self.active_node, self.remainder, txt_with_dollar)
                return
    
    #################################
    #    Traversal via skip count
    #################################
    def traverse(self, active_node: Node, remainder, txt_with_dollar) -> tuple[Node, tuple[int,int] | None]:
        if remainder == None:
            return active_node, None
        
        remainder_start, remainder_end = remainder
        skip_count_start = remainder_start
        curr_node = active_node

        #Performing skip counts until its no longer possible
        while skip_count_start <= remainder_end:
            start_char_index = ord(txt_with_dollar[skip_count_start]) - self.ALPHABET_START
            curr_edge_to_traverse = curr_node.children[start_char_index]
            edge_length = curr_edge_to_traverse.get_length()
            remaining_length = remainder_end - skip_count_start + 1
            #This would mean that the entire edge can be skipped over which allows us to get towards the next node instantly
            if remaining_length > edge_length:
                skip_count_start += edge_length
                curr_node = curr_edge_to_traverse.child_node
            # If the remaining length is smaller than the edge length then that means that we cant skip count further
            # and return back the most recent node we're standing on along with the remaining remainder that hasn't been
            # consumed
            else:
                return curr_node, (skip_count_start, remainder_end)
        #This means that we have directly landed on a node and there is no more remainder
        return curr_node, None
    
    ##############################
    #   Suffix extensions rules
    ##############################
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
    
    def rule_two_alternate(self, active_node: Node, start: int, end: End, txt_with_dollar) -> tuple[Node, None]:
        # Create the leaf node and also the edge that will connect to the leaf node
        leaf_node = self.create_new_leaf(suffix_index = start)
        edge_to_leaf_node = Edge(start, end, leaf_node)

        # Connect the active node to the leaf node via the created edge
        start_index_char = ord(txt_with_dollar[start]) - self.ALPHABET_START
        active_node.children[start_index_char] = edge_to_leaf_node

        # If the previous extension's pending node hasn't been resolved yet then the active node
        # for this extension will resolve it
        if self.pending_node is not None:
            self.pending_node.suffix_link = active_node
            self.pending_node = None

        # To prepare for the next extension we'll perform a suffix link traversal to the next active node 
        # via the suffix link and the remainder is still set as None for consistant return of active node, remainder
        new_active_node = active_node.suffix_link
        new_remainder = None
        
        return new_active_node, new_remainder
    
    def rule_three(self, new_active_node, new_remainder):
        self.active_node = new_active_node
        self.remainder = new_remainder
    
    def perform_extension(self, active_node, remainder, phase_i, txt_with_dollar):
        if remainder == None:
            start_char_index = ord(txt_with_dollar[phase_i]) - self.ALPHABET_START
            curr_edge_to_traverse = active_node.children[start_char_index]
            if curr_edge_to_traverse == None:
                self.rule_two_alternate(active_node)



    def create_new_leaf(self, suffix_index) -> Node:
        return Node(isLeaf=True, suffix_index= suffix_index)

    def create_new_internal_node(self) -> Node:
        return Node()
    



