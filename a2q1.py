# Ekrithyreach Lay
# Student ID: 33698759

import sys

#################################################################
# Data structure to support the construction of the suffix tree
#################################################################
class End:
    """
    The End data structure is used to repesent the global end value when performing ukkonen's so that
    all the nodes that are created can point to the same End.
    """
    def __init__(self, val=0):
        self.val = val

class Node:
    """
    The Node represents a node within the suffix tree where the children list holds edges to its 
    child nodes. If it's a leaf node then we'll set it to true along with the suffix index which 
    is the starting index of the suffix. Every internal node also has a suffix link as well pointing 
    towards another internal node with the exception of the root as it'll point towards itself
    """
    def __init__(self, suffix_link = None, isLeaf = False, isRoot = False, suffix_index = -1, node_id = 0):
        self.suffix_link: Node = suffix_link
        self.children = [None for _ in range(126-36+1)]
        self.isLeaf = isLeaf
        self.isRoot = isRoot
        self.suffix_index = suffix_index
        self.node_id = node_id # Used to keep track of the creation of the node where node 0 means that its made 
                               # before node 1 etc

class Edge:
    """
    The Edge contains a starting value in the form of an int whereas the end will either be an int or an End object. The reason
    why I did this is because edges that connects to a leaf node will have the end variable pointing to an End object in which case
    the End object will have it's values incremented from phase to phase.
    """
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
        self.remainder: tuple[int, int] = None # The tuple represents the start and end point of the remainder
        self.pending_node: Node = None # When a new node is created in extension j it's suffix link 
                                       # will be resolved in extension j+1
        
    def construct_suffix_tree(self, string):
        """
        The overall structure is obtained from the psuedocode provided in week 4 lecture notes on Ukkonen's algorithm. 
        By taking into account the different optimisation tricks such as suffix links, setting edge values to (start, end), 
        skip counting during traversal, phase stopper and the rapid leaf extension, the algorithm is then able to create a 
        suffix tree in O(n) space and time where n is the length of the string including the $ character. Each node can have
        at most 91 children which is constant. There are at most 2n-1 nodes and 2n-2 edges as well so summing them together 
        would mean that the space is bounded by O(n).
        """
        str_with_dollar = string + '$'
        n = len(str_with_dollar)

        # last_j represents the index of the latest rule 2 we've encountered as last_j + 1 must have encountered a 
        # rule 3 for phase i to stop. When starting, since no rule 2 has been spotted then I'll set it to -1.
        last_j = -1
        print("Root Node " + str(self.node_counter))
        for phase_i in range(n):
            self.global_end.val = phase_i
            print("\nPhase " + str(phase_i+1) + " starts from Extn " + str(last_j+2)) # The phase and extension is converted to 1 base indexing
            for extension_j in range(last_j+1, phase_i+1):
                # During each extension j, we'll pass in our current active node and remainder so that as the suffix tree
                # is traversing via skip count, a new active node and remainder will emerge. Depending on the value of the new 
                # remainder it will help us determine what type of extension to perform.
                self.active_node, self.remainder = self.traverse(self.active_node, self.remainder, str_with_dollar)
                extension_performed = self.perform_extension(self.active_node, self.remainder, phase_i, extension_j, str_with_dollar)
                if extension_performed == 3:
                    break
                else:
                    last_j += 1
    
    #################################
    #    Traversal via skip count
    #################################
    def traverse(self, active_node: Node, remainder, str_with_dollar):
        """
        The traversal algorithm takes in the current active node and remainder and will return back a new 
        active node and remainder after the skip count is performed.
        """
        if remainder == None:
            return active_node, None
        
        remainder_start, remainder_end = remainder
        skip_count_start = remainder_start
        curr_node = active_node

        # Performing skip counts until its no longer possible. skip count start keep tracks of how far we are when traversing
        # through the remaining string and we'll stop once we reach the end of the remainder.
        while skip_count_start <= remainder_end:
            start_char_index = ord(str_with_dollar[skip_count_start]) - self.ALPHABET_START
            curr_edge_to_traverse = curr_node.children[start_char_index]
            edge_length = curr_edge_to_traverse.get_length()
            remaining_length = remainder_end - skip_count_start + 1
            #This would mean that the entire edge can be skipped over, allowing us to go towards the next node instantly
            if remaining_length > edge_length:
                skip_count_start += edge_length
                curr_node = curr_edge_to_traverse.child_node
            # As the remaining_length is equal to the edge_length it means that the remainder has fully been consumed and
            # we're now currently standing on the next node which becomes the new active node for us to perform our 
            # extension on
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
    def rule_two_regular(self, active_node: Node, end: End, remainder: tuple[int, int], str_with_dollar, phase_i, extension_j) -> tuple[Node, (int, int)]:
        """
        Arguments:
            active_node: The node we're standing on as we perform the extension below

            end: the End object which is self.global_end, will be used when creating a new edge to a leaf node as going from one phase
                 to the next will implicitly cause rule 1 to occur

            remainder: The remaining amount to traverse so that we can perform the extension at index i, given that remainder will be from
                       str_with_dollar[k..i-1]

            str_with_dollar: The resulting string after the dollar character has been added at the end

            phase_i: The current phase we're at, useful as the edge to the new leaf will have it as the start point

            extension_j: The current extension we're at. It's used when we create our new leaf as the new leaf's suffix
                         index will be equal to extension j.
        
        Returns:
            new_active_node: the active node's suffix link which will be used for the next extension j+1 of phase i
            
            new_remainder: Either returns a tuple containing starting and ending index or None as it's possible to become None
                           when the root traverses to itself.
        """
        remainder_start, remainder_end = remainder
        remainder_length = remainder_end - remainder_start + 1

        # the edge we are splitting: find the child of active_node that remainder starts with
        first_char_index = ord(str_with_dollar[remainder_start]) - self.ALPHABET_START
        edge_that_need_to_split = active_node.children[first_char_index]
        index_at_split_end = edge_that_need_to_split.start + remainder_length - 1

        # Create a new internal node at the split point and also re-attach the edge's suffix
        # after the split point as it's child
        index_after_split_end = index_at_split_end + 1
        new_internal_node = self.create_new_internal_node()
        start_index_of_new_internal_node = ord(str_with_dollar[index_after_split_end]) - self.ALPHABET_START
        new_internal_node.children[start_index_of_new_internal_node] = Edge(index_after_split_end, edge_that_need_to_split.end, edge_that_need_to_split.child_node)

        # Creating a new leaf for the phase i character and attach it with the new internal node
        new_leaf = self.create_new_leaf(extension_j)
        new_leaf_index = ord(str_with_dollar[phase_i]) - self.ALPHABET_START
        edge_to_new_leaf = Edge(phase_i, end, new_leaf)
        new_internal_node.children[new_leaf_index] = edge_to_new_leaf

        # Replace the active node's old edge with an edge to the newly created internal node
        active_node.children[first_char_index] = Edge(edge_that_need_to_split.start, index_at_split_end, new_internal_node)

        # If the previous extension's pending node hasn't been resolved yet then the pending
        # node will form a sufffix link to the newly created internal node
        if self.pending_node is not None:
            print(f"        Linking Node {self.pending_node.node_id} to Node {active_node.node_id}")
            self.pending_node.suffix_link = new_internal_node
        
        # We'll set the new internal node as unresolved 
        self.pending_node = new_internal_node

        # We'll check if the active node is the root because if it is then it'll perform a suffix link to itself for the next
        # extension meaning that the remainder's first character will be removed whereas if the active node isn't the root then the 
        # remainder stays the same
        if active_node.isRoot:
            if remainder_start < remainder_end:
                new_remainder = (remainder_start + 1, remainder_end)
            else:
                new_remainder = None
        else:
            new_remainder = remainder
        
        # To prepare for the next extension we'll perform a suffix link traversal to the next active node 
        # via the suffix link
        new_active_node = active_node.suffix_link

        return new_active_node, new_remainder
    
    def rule_two_alternate(self, active_node: Node, start: int, end: End, str_with_dollar, extension_j) -> tuple[Node, None]:
        """
        Arguments:
            active_node: The node we're standing on as we perform the extension below

            start: the starting index of the edge to leaf node

            end: the End object which points towards self.global_end

            str_with_dollar: The resulting string after the dollar character has been added at the end

            extension_j: The current extension we're at. It's used when we create our new leaf as the new leaf's suffix
                         index will be equal to extension j.

        Returns:
            new_active_node: the active node's suffix link which will b eused for the extension j+1 of phase i

            remainder: None as in order to reach rule 2 alternate in the first place remainder must be None
        """
        # Create the leaf node and also the edge that will connect to the leaf node
        leaf_node = self.create_new_leaf(suffix_index = extension_j)
        edge_to_leaf_node = Edge(start, end, leaf_node)

        # Connect the active node to the leaf node via the created edge
        start_index_char = ord(str_with_dollar[start]) - self.ALPHABET_START
        active_node.children[start_index_char] = edge_to_leaf_node

        # If the previous extension's pending node hasn't been resolved yet then the active node
        # for this extension will resolve it
        if self.pending_node is not None:
            print(f"        Linking Node {self.pending_node.node_id} to Node {active_node.node_id}")
            self.pending_node.suffix_link = active_node
            self.pending_node = None

        # To prepare for the next extension we'll perform a suffix link traversal to the next active node 
        # via the suffix link and the remainder is still set as None for consistant return of a Node and remainder
        new_active_node = active_node.suffix_link
        new_remainder = None
        
        return new_active_node, new_remainder
    
    def rule_three(self, new_active_node, new_remainder):
        """
        As the character at index i of phase i extension j already exists within the edge we'll simply return back the 
        same active_node and remainder as phase i+1 of the same extension could possibly yield a rule 2 or 3.
        """
        # If the previous extension's pending node hasn't been resolved yet then the active node 
        # for the extension will resolve it
        if self.pending_node is not None:
            print(f"        Linking Node {self.pending_node.node_id} to Node {new_active_node.node_id}")
            self.pending_node.suffix_link = new_active_node
            self.pending_node = None

        return new_active_node, new_remainder
    
    #################################
    #  Which Extensions to Perform?
    #################################
    def perform_extension(self, active_node: Node, remainder, phase_i: int, extension_j: int, str_with_dollar: str) -> int:
        """
        After a traversal we'll have an active node that we're standing on along with some remainder. This remainder 
        is key in allowing us to determine what extension we'll need to do.

        Say we're in extension j of phase i, if we see that the remainder is None then it means that we can immediatly check
        if the active node has an edge that starts with the ith character since we need to extend everything in the implcit 
        suffix tree with the ith character. If it doesn't exist then we'll need to perform a rule 2 alternate as we only 
        need to create a new edge and leaf node where the edge contains the ith character. Else we dont do anything since 
        the ith character already exists (rule 3).
    
        On the otherhand if there is some remaining value [remainder_start = k, remainder_end = i - 1] then that means that 
        our extension will occur somewhere along the edge. We can use the remainder to traverse across a portion of the edge 
        immediatly which lands us on some character c. If this character c doesn't match with our ith character then we'll 
        have to perform a rule 2 regular extension. Else we dont do anything which is rule 3, same as above.

        After we're done with our extension we'll return either 2 or 3. 3 would mean that a rule 3 occured so we'll need to 
        stop the current phase i and go to phase i+1, whereas rule 2 would allow us to increment last_j for the next phase 
        as 0 to last_j(inclusive) implies a rule 1 in the next phase i+1 which is why the inner for loop of 
        construct_suffix_tree(self,string) starts at last_j+1
        """
        if remainder == None:
            start_char_index = ord(str_with_dollar[phase_i]) - self.ALPHABET_START
            curr_edge_to_traverse = active_node.children[start_char_index]
            if curr_edge_to_traverse == None:
                print(f'    Extn {extension_j+1} applies Rule 2 (alternate)')
                print(f'    Active Node = Node {self.active_node.node_id} (suffix link to Node {self.active_node.suffix_link.node_id}); Remainder = {self.remainder_to_str_for_runLog(remainder)}')
                self.active_node, self.remainder = self.rule_two_alternate(active_node, phase_i, self.global_end, str_with_dollar, extension_j)
                return 2
            else:
                print(f'    Extn {extension_j+1} applies Rule 3')
                print(f'    Active Node = Node {self.active_node.node_id} (suffix link to Node {self.active_node.suffix_link.node_id}); Remainder = {self.remainder_to_str_for_runLog(remainder)}')
                self.active_node, self.remainder = self.rule_three(active_node, (phase_i, phase_i))
                return 3
        else:
            remainder_start, remainder_end = remainder
            first_char_index = ord(str_with_dollar[remainder_start]) - self.ALPHABET_START

            curr_edge_to_traverse = active_node.children[first_char_index]
            next_char_pos = curr_edge_to_traverse.start + (remainder_end - remainder_start + 1)

            if str_with_dollar[next_char_pos] != str_with_dollar[phase_i]:
                print(f'    Extn {extension_j+1} applies Rule 2 (regular)')
                print(f'    Active Node = Node {self.active_node.node_id} (suffix link to Node {self.active_node.suffix_link.node_id}); Remainder = {self.remainder_to_str_for_runLog(remainder)}')
                self.active_node, self.remainder = self.rule_two_regular(active_node, self.global_end, remainder, str_with_dollar, phase_i, extension_j)
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
        """
        A simple function used determine how the remainder should be outputed where we'll need to return
        the string EMPTY for an empty remainder or the other string shown below to show where the remainder
        starts and ends
        """
        if remainder == None:
            return "EMPTY"
        else:
            remainder_start, remainder_end = remainder
            return f"S[{remainder_start+1}...{remainder_end+1}]"

    def create_new_leaf(self, suffix_index) -> Node:
        self.node_counter += 1
        print(f"        Node {self.node_counter} created: Leaf node!")
        return Node(isLeaf=True, suffix_index= suffix_index, node_id=self.node_counter)

    def create_new_internal_node(self) -> Node:
        self.node_counter += 1
        print(f"        Node {self.node_counter} created: Internal node!")
        return Node(node_id=self.node_counter)
    
    #########################
    #   Depth First Search
    #########################
    def depth_first_search(self, node: Node, parent_depth: int, edge_length: int, lcp_depth: int):
        """
        The algorithm is a recursive depth first search where our base case is determining wether the node
        we're standing on is a leaf or not. A node's children is contained within a list that's in lexicographic order
        so as we run dfs on the suffix tree and return suffix indexes of each leaf nodes we'll then get our suffix array.

        To find LCP[i] it'll be the depth of the lowest commmon ancestor between suffix_array[i] and suffix_array[i-1].
        During depth first search we'll classify a node's children into 2 types being the first child from it's parent node
        or not.
        
        If it is and also a leaf node then this tells us that the LCP between suffix_array[i] and suffix_array[i-1] 
        is determined by an ancestor above, either it's the parent node, the parent's parent and so on... We'll need to pass 
        this information through our traversal which is why we have the lcp_depth which tracks the lowest depth between
        suffix_array[i-1] and our eventual suffix_array[i].
        
        If a child node is not the first child and it's also a leaf node then that means that the previous suffx i-1 that
        we have traversed through must also go through the parent node which makes the parent the lowest common ancestor
        to both suffix i-1 and suffix i.

        Time Complexity: O(V+E) where V is the number of nodes or vertices and E are the number of edges 
        Space Complexity: As the tree's already been constructed for the traversal, the only space that is created is from
                          the recursion calls for V nodes and also the result array containing C leafs. Therefore 
                          space complexity becomes O(V+C) where V is the number of nodes and C are the number of leafs.
        """
        current_depth = parent_depth + edge_length
        # Base case: The node we're at is the leaf node so we cant go further than this
        if node.isLeaf:
            return [lcp_depth]
        result = []
        first_child = True
        for edge in node.children:
            if edge is not None:
                if first_child:
                    # The lcp of the first child leaf node i isn't determined by the current depth of the parent as 
                    # it's previous leaf node i-1 comes from a different subtree where the lca may be the parent,
                    # the parent's parent and so on. As a result we'll pass the lcp_depth unchanged.
                    result += self.depth_first_search(edge.child_node, current_depth, edge.get_length(), lcp_depth)
                    first_child = False
                else:
                    # We'll pass the current_depth of the parent to leaf node i as leaf node i and leaf node i-1 share
                    # the same lca which is the parent.
                    result += self.depth_first_search(edge.child_node, current_depth, edge.get_length(), current_depth)
        return result

############################
# Finding the LCP via DFS
############################
def compute_for_LCP(string):
    """
    We'll first construct a suffix tree using ukkonen's algorithm and after that we'll run depth first search
    starting from the root node which returns an array of values containing the lcp for each suffix.

    Time Complexity: Given n is the length of the string appended with $, the time complexity comes from the summation 
                     of time needed to create the suffix tree(with ukkonen's) and depth first search on it. Creating the 
                     suffix tree takes O(n) time and dfs on the suffix tree takes O(n) times as well as a suffix tree has 
                     at most 2n-1 nodes and 2n-2 edges. Keep in mind that each node only has at most 91 children so the for 
                     loop running inside dfs is constant for that particular node. Finally we got O(n+n) = O(n).
    
    Space Complexity: The space complexiy comes from running both algorithm mentioned above so the space it takes to hold and
                      construct the suffix tree is O(n) given there are at most 2n-1 nodes and 2n-2 edges. Each node within
                      the suffix tree contains at most 91 children which is constant. The recursion stack within dfs is 
                      bounded by 2n-1 nodes and n leaves to hold the resulting lcp array. As a result we'll get 
                      O(n+n+n) = O(n).
    """

    # Redirecting the print statements produced during suffix tree construction inot the runlog txt file
    # learned from https://stackoverflow.com/questions/7152762/how-to-redirect-print-output-to-a-file
    with open('runlog_a2q1.txt', 'w') as f:
        sys.stdout = f
        ukkonen = Ukkonen_algorithm()
        ukkonen.construct_suffix_tree(string)
        sys.stdout = sys.__stdout__

    lcp_array = ukkonen.depth_first_search(ukkonen.root, 0, 0, 0)
    
    return lcp_array

# The overall code has been obtained from the Command-line usage tutorial for Assignments
# with the modification with the readlines() to readline() as the pattern and text txt files 
# only contain stuff in the first line.
def read_file(file_path: str) -> str:
    f = open(file_path, 'r')
    line = f.readline()
    f.close()
    return line

# The overall code has been obtained from the Command-line usage tutorial for Assignments
if __name__ == '__main__':
    _, filename1 = sys.argv

    #retrieve the file paths from the commandline arguments
    string_to_compute = read_file(filename1)

    lcp_array = compute_for_LCP(string_to_compute)

    # Learned how to open a text file and write into it from 
    # https://www.w3schools.com/python/python_file_write.asp
    with open("output_a2q1.txt", 'w') as f:
        for index in range(len(lcp_array)):
            f.write(str(lcp_array[index]) + '\n')
