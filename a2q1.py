# Ekrithyreach Lay
# Student ID: 33698759

#################################################################
# Data structure to support the construction of the suffix tree
#################################################################
class End:
    def __init__(self, val=0):
        self.val = val

class Node:
    def __init__(self, suffix_link = None, isLeaf = False, isRoot = False, suffix_index = -1, node_id = 0):
        self.suffix_link: Node = suffix_link
        self.children = [None for _ in range(126-36+1)]
        self.isLeaf = isLeaf
        self.isRoot = isRoot
        self.suffix_index = suffix_index
        self.node_id = node_id #Used to keep track of the creation of the node where 0 means that its made before 1 etc

class Edge:
    def __init__(self, start: int, end, child_node: Node):
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
        self.node_counter = 1 # For the created root node
        self.root = Node(isLeaf = False, isRoot= True, node_id=self.node_counter)
        self.root.suffix_link = self.root
        self.ALPHABET_START = 36
        self.ALPHABET_END = 126
        self.global_end = End(0)
        self.active_node: Node = self.root
        self.remainder: tuple[int, int] = None
        self.pending_node: Node = None # When a new node is created in extension j it's suffix link 
                                      # will be resolved in extension j+1
        
    def construct_suffix_tree(self, txt):
        txt_with_dollar = txt + '$'
        n = len(txt_with_dollar)
        last_j = 0
        print("Root Node " + str(self.node_counter))
        for phase_i in range(n):
            self.global_end.val = phase_i
            print("Phase " + str(phase_i+1) + " starts from Extn " + str(last_j+1)) # The phase and extension is converted to 1 base indexing
            for extension_j in range(last_j, phase_i+1):
                self.active_node, self.remainder = self.traverse(self.active_node, self.remainder, txt_with_dollar)
                extension_performed = self.perform_extension(self.active_node, self.remainder, phase_i, extension_j, txt_with_dollar)
                if extension_performed == 3:
                    break
                else:
                    last_j += 1
    
    #################################
    #    Traversal via skip count
    #################################
    def traverse(self, active_node: Node, remainder, txt_with_dollar):
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
            # As the remaining_length is equal to the edge_length it means that the remainder has fully been consumed and
            # we're now currently standing on next node which becomes the new active node for us to perform our extensions on
            elif remaining_length == edge_length:
                return curr_edge_to_traverse.child_node, None
            # If the remaining length is smaller than the edge length then that means that we cant skip count further
            # and return back the most recent node we're standing on along with the remaining remainder that hasn't been
            # consumed
            else:
                return curr_node, (skip_count_start, remainder_end)
    
    ##############################
    #   Suffix extensions rules
    ##############################
    def rule_two_regular(self, active_node: Node, end: End, remainder: tuple[int, int], txt_with_dollar, phase_i) -> tuple[Node, (int, int)]:
        remainder_start, remainder_end = remainder
        remainder_length = remainder_end - remainder_start + 1

        # the edge we are splitting: find the child of active_node that remainder starts with
        first_char_index = ord(txt_with_dollar[remainder_start]) - self.ALPHABET_START
        edge_that_need_to_split = active_node.children[first_char_index]
        index_at_split_end = edge_that_need_to_split.start + remainder_length - 1

        # Creating a new edge from the internal node and attach it to the old child
        index_after_split_end = index_at_split_end + 1
        new_internal_node = self.create_new_internal_node()
        start_index_of_new_internal_node = ord(txt_with_dollar[index_after_split_end]) - self.ALPHABET_START
        new_internal_node.children[start_index_of_new_internal_node] = Edge(index_after_split_end, edge_that_need_to_split.end, edge_that_need_to_split.child_node)

        # Creating a new leaf for the phase i character and attach it with the new internal node
        new_leaf = self.create_new_leaf(phase_i)
        new_leaf_index = ord(txt_with_dollar[phase_i]) - self.ALPHABET_START
        edge_to_new_leaf = Edge(phase_i, end, new_leaf)
        new_internal_node.children[new_leaf_index] = edge_to_new_leaf

        # Replace the active node's old edge with an edge to the newly created internal node
        active_node.children[first_char_index] = Edge(edge_that_need_to_split.start, index_at_split_end, new_internal_node)

        # If the previous extension's pending node hasn't been resolved yet then the pending
        # node will form a sufffix link to the newly created internal node
        if self.pending_node is not None:
            self.pending_node.suffix_link = new_internal_node
        
        # We'll set the new internal node as unresolved 
        self.pending_node = new_internal_node

        # We'll check if the active node is the root because if it is then it'll perform a suffix link to itself within the next
        # extension meaning that the remainder's first character will be removed whereas if the active node isn't the root then the 
        # remainder stays the same
        if active_node.isRoot:
            if remainder_start < remainder_end:
                new_remainder = (remainder_start + 1, remainder_end)
            else:
                new_remainder = None
        else:
            new_remainder = remainder

        return active_node.suffix_link, new_remainder
    
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

        # If the previous extension's pending node hasn't been resolved yet then the active node 
        # for the extension will resolve it
        if self.pending_node is not None:
            self.pending_node.suffix_link = new_active_node
            self.pending_node = None

        return new_active_node, new_remainder
    
    def perform_extension(self, active_node: Node, remainder, phase_i: int, extension_j: int, txt_with_dollar: str) -> int:
        if remainder == None:
            start_char_index = ord(txt_with_dollar[phase_i]) - self.ALPHABET_START
            curr_edge_to_traverse = active_node.children[start_char_index]
            if curr_edge_to_traverse == None:
                print(f'    Extn {extension_j+1} applies Rule 2 (alternate)')
                print(f'    Active Node = Node {self.active_node.node_id} (suffix link to Node {self.active_node.suffix_link.node_id}); Remainder = {self.remainder_to_str_for_runLog(remainder)}')
                self.active_node, self.remainder = self.rule_two_alternate(active_node, phase_i, self.global_end, txt_with_dollar)
                return 2
            else:
                print(f'    Extn {extension_j+1} applies Rule 3')
                print(f'    Active Node = Node {self.active_node.node_id} (suffix link to Node {self.active_node.suffix_link.node_id}); Remainder = {self.remainder_to_str_for_runLog(remainder)}')
                self.active_node, self.remainder = self.rule_three(active_node, (phase_i, phase_i))
                return 3
        else:
            remainder_start, remainder_end = remainder
            first_char_index = ord(txt_with_dollar[remainder_start]) - self.ALPHABET_START

            curr_edge_to_traverse = active_node.children[first_char_index]
            next_char_pos = curr_edge_to_traverse.start + (remainder_end - remainder_start + 1)

            if txt_with_dollar[next_char_pos] != txt_with_dollar[phase_i]:
                print(f'    Extn {extension_j+1} applies Rule 2 (regular)')
                print(f'    Active Node = Node {self.active_node.node_id} (suffix link to Node {self.active_node.suffix_link.node_id}); Remainder = {self.remainder_to_str_for_runLog(remainder)}')
                self.active_node, self.remainder = self.rule_two_regular(active_node, self.global_end, remainder, txt_with_dollar, phase_i)
                return 2
            else:
                print(f'    Extn {extension_j+1} applies Rule 3')
                print(f'    Active Node = Node {self.active_node.node_id} (suffix link to Node {self.active_node.suffix_link.node_id}); Remainder = {self.remainder_to_str_for_runLog(remainder)}')
                self.active_node, self.remainder = self.rule_three(active_node, (remainder_start, remainder_end + 1))
                return 3
    
    ############################
    #     Helper functions
    ############################
    def remainder_to_str_for_runLog(self, remainder):
        if remainder == None:
            return "EMPTY"
        else:
            remainder_start, remainder_end = remainder
            return f"S[{remainder_start+1}...{remainder_end+1}]"

    def create_new_leaf(self, suffix_index) -> Node:
        self.node_counter += 1
        print(f"        Node {self.node_counter} created: Leaf Node!")
        return Node(isLeaf=True, suffix_index= suffix_index, node_id=self.node_counter)

    def create_new_internal_node(self) -> Node:
        self.node_counter += 1
        print(f"        Node {self.node_counter} created: Leaf Node!")
        return Node(node_id=self.node_counter)
    
    #########################
    #   Depth First Search
    #########################
    def depth_first_search(self, node: Node) -> list[int]:
        return
    
    
ukkonen = Ukkonen_algorithm()
# ukkonen.construct_suffix_tree("googol")
ukkonen.construct_suffix_tree("abbbbcbbcbcabbbb")