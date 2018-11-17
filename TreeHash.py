#!/usr/bin/python3

import sys
import logging
import pdb

from math import log, pow, floor
# from hashlib import sha256 as sha
from hashlib import sha1 as sha

class Node(object):
    def __init__(self, height = -1, hash = None):
        self.height = height
        self.hash = hash

class TreeHash(object):
    """
    Calculate root hash of a tree of hashes
    """

    def __init__(self, hashes=None):
        self.root_hash = None
        self.logger = None
        self.height = -1    # tree height
        self.leaves = 0

        if not self.logger:
            self._init_logger()

        # update tree info
        hashes_len = 0
        if not hashes:
            return
        else:
            hashes_len = len(hashes)
        if hashes_len % 2:
            hashes_len += 1
        self._set_height(hashes_len)
        self.leaves = int(pow(2, self.height))  # number of leaf nodes is
                                                # always a pow of 2

        self.leaf_index = 0
        self._init_stack(hashes[self.leaf_index])
        self.leaf_index += 1

        self.root_hash = self.update_stack(hashes)

        self.logger.info("Tree Hash created")

    def _init_logger(self):
        # create logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        self.logger.addHandler(ch)

    
    def _set_height(self, n):
        """
        some tree information
        """
        height = log(n, 2)
        if height - floor(height) > 0.0:
            # height is not a whole number
            self.height = floor(height) + 1
        else:
            self.height = int(height)


    def _init_stack(self, hash):
        #
        # a stack of TreeHash is a list of Node objects
        #
        self.stack = []
        # add a node of height 0
        self._add_node_to_stack(0, hash)


    def _add_node_to_stack(self, height, hash):
        #
        # add a node with height height to stack
        #
        self.stack.append(Node(height, hash))

    def update_stack(self, hashes):
        while (len(hashes) < self.leaves):
            # in case number of items in hashes is not a pow of 2, pad
            # hashes with the last one
            hashes.append(hashes[-1])

        while (True):
            if len(self.stack) < 2 or self.stack[-1].height != self.stack[-2].height:
                # not ready to calculate parent node hash yet. add a node of height 0 to stack
                self._add_node_to_stack(0, hashes[self.leaf_index])
                self.leaf_index += 1
            else:   # calculate parent node hash, (and throw away leaf nodes)
                n1 = self.stack.pop()
                n2 = self.stack.pop()
                if (n1.height + 1) == self.height:  # we are at root
                    # return the root hash
                    return sha((n2.hash + n1.hash).encode('utf-8')).hexdigest()
                else:
                    self._add_node_to_stack(n1.height + 1, sha((n2.hash
                        + n1.hash).encode('utf-8')).hexdigest())


    def get_root_hash(self):
        return self.root_hash


if __name__ == '__main__':
    python_version = sys.version_info
    if python_version[0] < 3:
        print("Python version: {}. Must be run with python3".format(python_version))
        sys.exit(0)

    strings = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
               'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    hs = [sha(s.encode('utf-8')).hexdigest() for s in strings]
    th = TreeHash(hashes=hs)
    th.logger.info('hashes before Tree Hash: {0}\n'.format(hs))
    th.logger.info('hashes height: {}; tree leaves: {}\n'.format(th.height,
        th.leaves))
    th.logger.info('root hash: {0}\n'.format(th.get_root_hash()))
