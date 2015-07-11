#
#

import sys
import logging
import pdb

from math import log, pow, floor
# from hashlib import sha256 as sha
from hashlib import sha1 as sha

class MerkleTree:

    def __init__(self, hashes=None):
        """
        Create a Merkle hash tree
        """
        self.root_hash = None
        self.logger = None
        if hashes is not None:
            hashes_len = len(hashes)
        if hashes_len > 0:
            if hashes_len % 2:
                hashes_len += 1
            self._set_tree_height(hashes_len)
            self._init_tree(self.height)
            self._build_tree(hashes)
            self.root_hash = self.tree[0]

            if not self.logger:
                self._init_logger()

#           pdb.set_trace()
            self.logger.info("Merkle Tree created")

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

    
    def _set_tree_height(self, n):
        height = log(n, 2)
        if height - floor(height) > 0.0:
            # height is not a whole number
            self.height = int(height) + 1
        else:
            self.height = int(height)


    def _init_tree(self, height):
        # Merkle Tree is a binary tree
        # where hashes are held only at leaves
        # for a tree of height height, the
        # total number of nodes is 2^(height + 1) - 1
        #
        # the tree is implemented as a list
        #
        treesize = int(pow(2, height + 1) - 1)
        self.tree = ['' ] * treesize


    def _build_tree(self, hashes):
        hashes_len = len(hashes)
        treesize = int(pow(2, self.height + 1) - 1)
        number_of_leaves = int(pow(2, self.height))
        start = number_of_leaves - 1
        # hashes are held at leaves
        for i in range(start, start + hashes_len):
            self.tree[i] = hashes[i - start]
        # fill the rest leaves with the last hash value
        for i in range(start + hashes_len, treesize):
            self.tree[i] = hashes[hashes_len - 1]

        # higher level hashes from leaves
        for level in range(self.height, 0, -1):
            for i in range(int(pow(2, level) - 1), int(pow(2, level + 1) - 2), 2):
                #print >> sys.stderr,"merkle: data offset",offset
                (parentstartoffset, j) = self._get_parent_offset(i, level)
                data = self.tree[i] + self.tree[i + 1]
                d = sha(data)
                self.tree[j] = d.hexdigest()


    def _get_parent_offset(self, i, level):
        parentstartoffset = int(pow(2, level) - 1)
        mystartoffset = int(pow(2, level + 1) - 1)
        j = parentstartoffset + (i - mystartoffset) / 2
        return (parentstartoffset, j)


    def _get_uncle_offset(self, offset, level):
        if level == 1:
            return 0
        [parentstartoffset, parentoffset ] = self._get_parent_offset(offset, level - 1)
        parentindex = parentoffset - parentstartoffset
        if parentoffset % 2 == 0:
            uncleoffset = parentoffset - 1
        else:
            uncleoffset = parentoffset + 1
        return uncleoffset

    def get_root_hash(self):
        return self.root_hash

    def compare_root_hashes(self, hash):
        return self.root_hash == hash

    def get_hashes(self, index):
        start = int(pow(2, self.height) - 1)
        offset = start + index
        # 1. Add piece's own hash
        hashlist = [ [offset, self.tree[offset]] ]
        # 2. Add hash of piece's sibling, left or right
        if offset % 2 == 0:
            siblingoffset = offset - 1
        else:
            siblingoffset = offset + 1
        if siblingoffset != -1:
            hashlist.append([siblingoffset, self.tree[siblingoffset]])
        # 3. Add hashes of uncles
        uncleoffset = offset
        for level in range(self.height, 0, -1):
            uncleoffset = self._get_uncle_offset(uncleoffset, level)
            hashlist.append( [uncleoffset, self.tree[uncleoffset]] )
        return hashlist


    def check_hashes(self, hashlist):
        return self.check_tree_path(hashlist)


    def check_tree_path(self, hashlist):
        maxoffset = int(pow(2, self.height + 1) - 2)
        mystartoffset = int(pow(2, self.height) - 1)
        i = 0
        a = hashlist[i]
        if a[0] < 0 or a[0] > maxoffset:
            return False
        i += 1
        b = hashlist[i]
        if b[0] < 0 or b[0] > maxoffset:
            return False
        i += 1
        myindex = a[0] - mystartoffset
        sibindex = b[0] - mystartoffset
        for level in range(self.height, 0, -1):
            a = check_fork(a, b, level)
            b = hashlist[i]
            if b[0] < 0 or b[0] > maxoffset:
                return False
            i += 1
        if a[1] == root_hash:
            return True
        else:
            return False


if __name__ == '__main__':
    hs = []
    strings = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q']
    for i in range(0, 13):
        d = sha(strings[i])
        hs.append(d.hexdigest())
    mt = MerkleTree(hashes=hs)
    mt.logger.info('hashes before Merkle Tree: {0}\n'.format(hs))
    mt.logger.info('root hash: {0}\n'.format(mt.get_root_hash()))
    mt.logger.info('Merkle Tree hashes: {0}\n'.format(mt.tree))
    mt.logger.info('Merkle Tree hashes @ {0}: {1}\n'.format(3, mt.get_hashes(3)))
