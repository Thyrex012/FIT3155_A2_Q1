class Node:
    def __init__(self, start:int, end:int, suffix_link = None, isLeaf = False):
        self.start = start
        self.end = end
        self.suffix_link = suffix_link
        self.children = [None for _ in range(126-36+1)]
        self.isLeaf = isLeaf

class Ukkonen_algorithm:
    def __init__(self):
        pass

    def add_edge()
