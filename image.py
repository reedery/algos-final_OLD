"""
Image object class for an image w/ methods
@authors: danielle nash, ryan reede, drew hoo
12/08/16
"""
import numpy as np


class Image(object):
    def __init__(self, data): # data is an np.array
        self.data = data
        self.width = len(data[0])
        self.height = len(data)
        self.bounded = None  # do not call bound until after denoise
        self.inverted = None  # TODO set this param
        # self.isPolygon = self.getType()  # false = mnist?

    def writeOut(self, path, filename, version='full'):
        """"
        output the file to a .txt, given and path and filename
        version can either be 'full' or 'bounded'
        """
        file = open(path + '/' + filename + '.txt', "w")
        data = self.data if version == 'full' else self.bounded
        for row in data:
            file.write("\n")
            for item in row:
                file.write(str(item) + " ")
        file.close()

    def encodeValues(self, vals):
        """"
        Determine if the values given as input are all ONE,
        ZERO or MIX. Encoded as follows:
            00 = all ZERO, 01 = MIX and 11 = all ONE
        """
        if vals.count(vals[0]) == len(vals):
            if vals[0] == 0:
                return '00'
            return '11'
        return '01'

    def checkWindow(self, posY, posX):
        # TODO: Parameterize this function for variable window sizes (not just 4)
        """"
        Checks 4x4 matrix from around specified X and Y coords
            that wraps around any edge of the given image's
            data matrix for noise removal. Will check
        Returns:
            - 4x4 matrix from around specified X and Y coords
                that wraps around any edge of the given image's
                data matrix for noise removal.
            - list of x/y indices that are in the middle of the
                4x4 matrix
            - 2-bit encoding where 00 = all ZERO, 01 = MIX and
                11 = all ONE. These values refer to what is on
                the outside edges of the 4x4 matrix
        """
        data = self.data
        height = self.height
        width = self.width
        outsideValues, insideIndices, final = [], [], []
        for c in range(4):
            posX_new = (posX + c) % height
            c_list = []
            for r in range(4):
                posY_new = (posY + r) % width
                c_list.append(data[posX_new][posY_new])
                if r == 1 or r == 2: # check to make sure we're in the middle
                    if c == 1 or c == 2:
                        insideIndices.append([posY_new, posX_new])
            final.append(c_list)
            if c == 0 or c == 3:
                outsideValues.extend(c_list)
            else:
                outsideValues.extend([c_list[0], c_list[3]])
        return final, insideIndices, self.encodeValues(outsideValues)

    def changeValues(self, indices, number):
        """"
        reassign all values to 'number' in 'indices'
        """
        for xyPair in indices:
            self.data[xyPair[1]][xyPair[0]] = number

    def denoise(self):
        # TODO: Parameterize this function for variable window sizes (not just 4)
        """
        Iterate though each pixel of the image, create a 4x4
        window with this pixel at the top left corner, and
        remove chunks of disconnected noise
        """
        # make 4x4 chunks, if center is dif from surrounding, make it the same as surrounding.
        for w in range(0, self.width):
            for h in range(0, self.height):
                final, insides, code = self.checkWindow(w, h, self)
                if code != '01':
                    if code == '00':
                        self.changeValues(self, insides, 0)
                    else:
                        self.changeValues(self, insides, 1)

    # Initiate the search
    def search(self, padding=2, invert=False):
        """"
        add description
        """
        rows, cols = np.shape(self.data)
        left_col, top_row = self.start_top(self.data, rows, cols, True)
        right_col, bot_row = self.start_bot(self.data, rows, cols, True)

        # RESHAPE with the new dims
        r1 = top_row - padding if top_row - padding > 0 else top_row
        r2 = bot_row + padding if bot_row - padding > 0 else bot_row
        c1 = left_col - padding if left_col - padding > 0 else left_col
        c2 = right_col + padding if right_col + padding > 0 else right_col

        row_idx = np.array([x for x in range(r1, r2)])
        col_idx = np.array([x for x in range(c1, c2)])

        # MAKE SURE WERE NOT ON THE EDGES OR OVER THE INDEXING
        if col_idx[-1] == cols:
            col_idx = np.delete(col_idx, -1)

        if row_idx[-1] == rows:
            row_idx = np.delete(row_idx, -1)

        # pdb.set_trace()
        # new_image = image[row_idx[:, None], col_idx]
        # print new_image
        # pdb.set_trace()
        # return new_image
        # pdb.set_trace()
        self.bounded = self.data[row_idx[:, None], col_idx]

        """
        row_idx = np.array([0, 1, 3])
        col_idx = np.array([0, 2])
        a[row_idx[:, None], col_idx]
        """

    # Top always starts at 0,0
    def start_top(self, rows, cols, invert=False):
        """"
        add description
        """
        left_col = []
        top_row = []
        flag = False
        i = 0
        j = 0
        x, y = False, False
        while not flag:
            while i < rows and j < cols:
                x, y = self.search_row(i, invert), self.search_col(j, invert)
                if x:
                    top_row.append(i)
                if y:
                    left_col.append(j)
                if x == True and y == True:
                    flag = True
                i += 1
                j += 1
            flag = True
        # Assumes we found something
        return left_col[0], top_row[0]

    # Bot always starts at shape - 1
    def start_bot(self, rows, cols, invert=False):
        """"
        add description
        """
        right_col = []
        bot_row = []
        i = rows - 1
        j = cols - 1
        flag = False
        x, y = False, False
        while (not flag):
            while i > 0 and j > 0:
                x, y = self.search_row(i, invert), self.search_col(j, invert)
                if x:
                    bot_row.append(i)
                if y:
                    right_col.append(j)
                if x and y:
                    flag = True
                i -= 1
                j -= 1
            flag = True
        # Assumes we found something
        return right_col[0], bot_row[0]

    def search_row(self, i, invert):
        """"
        add description
        """
        fg = 1
        if invert:
            fg = 0

        row = self.data[i, :]
        # SEARCHES SOLELY FOR 1 ans the "other"
        found = np.argwhere(row == fg)
        # print 'found: ', found
        if len(set(found.flatten())) > 1:
            return True
        else:
            return False

            # for x in row:
            #     # TEMP => ADJUST FOR LATER

            #     if x == 1:
            #         return
            # return

    def search_col(self, j, invert):
        """"
        add description
        """
        fg = 1
        if invert:
            fg = 0
        col = self.data[:, j]
        # SEARCHES SOLELY FOR 1 ans the "other"
        found = np.argwhere(col == fg)
        # print 'found: ', found
        if len(set(found.flatten())) > 1:
            return True
        else:
            return False