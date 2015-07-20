#
#

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

    def __init__(self, hashes=None):
        """
        Create a tree hash
        """
        self.root_hash = None
        self.logger = None
        if hashes is not None:
            hashes_len = len(hashes)
        if hashes_len > 0:
            if hashes_len % 2:
                hashes_len += 1
            self.leaf = 0
            if not self.logger:
                self._init_logger()
            self._init_stack(hashes[self.leaf])
            self.leaf += 1

            self._set_height(hashes_len)
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
        height = log(n, 2)
        if height - floor(height) > 0.0:
            # height is not a whole number
            self.height = int(height) + 1
        else:
            self.height = int(height)
        # now self.leaves is a power of 2
        self.leaves = int(pow(2, self.height))


    def _init_stack(self, hash):
        #
        # a stack of TreeHash is a python list of Node objects
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
            hashes.append(hashes[-1])

        while (True):
            if len(self.stack) < 2 or self.stack[-1].height != self.stack[-2].height:
                # add a node of height 0 to stack
                self._add_node_to_stack(0, hashes[self.leaf])
                self.leaf += 1
            else:
                n1 = self.stack.pop()
                n2 = self.stack.pop()
                if (n1.height + 1) == self.height:
                    # return the root hash
                    return sha(n2.hash + n1.hash).hexdigest()
                else:
                    self._add_node_to_stack(n1.height + 1, sha(n2.hash + n1.hash).hexdigest())


    def get_root_hash(self):
        return self.root_hash


if __name__ == '__main__':
    hs = []
    strings = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q']
    for i in range(0, 13):
        d = sha(strings[i])
        hs.append(d.hexdigest())
    th = TreeHash(hashes=hs)
    th.logger.info('hashes before Tree Hash: {0}\n'.format(hs))
    th.logger.info('root hash: {0}\n'.format(th.get_root_hash()))
