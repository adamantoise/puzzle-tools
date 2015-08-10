"""
Polyomino Solver

Copyright (c) 2012, Adam Rosenfield
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice, this
    list of conditions and the following disclaimer.
    
    Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import operator
import os
import random
import subprocess
import struct
import sys

class PolyominoPuzzle:
    """Class representing one instance of a polyomino puzzle"""

    def __init__(self, filename):
        self.width = -1
        self.height = -1
        self.allow_rotations = True
        self.allow_reflections = False
        self.pieces = []
        self.piece_trans = []
        self.piece_bbs = []
        self._read_puzzle(filename)

    def _read_puzzle(self, filename):
        with open(filename) as f:
            state = 'header'
            for line in f:
                line = line.lower()
                # Ignore whitespace lines or lines that start with a hash
                if len(line.strip()) == 0 or line[0] == '#':
                    continue
                if state == 'header':
                    grid_type, w, h = line.split()
                    self.width = int(w)
                    self.height = int(h)
                    self.initial_grid = [[0 for j in range(self.width)] for i in range(self.height)]
                    if grid_type == 'rect':
                        state = 'puzzle'
                    elif grid_type == 'custom':
                        state = 'grid'
                        cur_y = 0
                        cur_x = 0
                    else:
                        raise Exception('Invalid grid type: %s' % grid_type)
                elif state == 'grid':
                    for c in line:
                        if c in '01':
                            self.initial_grid[cur_y][cur_x] = ord(c) - ord('0')
                            cur_x += 1
                            if cur_x == self.width:
                                cur_x = 0
                                cur_y += 1
                                if cur_y == self.height:
                                    state = 'puzzle'
                                    break
                elif state == 'puzzle':
                    # Check for some special rules tokens
                    token = line.strip()
                    if token == 'no_rotations':
                        self.allow_rotations = False
                        self.allow_reflections = False
                    elif token == 'allow_reflections':
                        self.allow_reflections = True
                    else:
                        # Puzzle piece description
                        piece_type, desc = line.split(' ', 1)
                        desc = desc.strip()
                        if piece_type == 'd':
                            self._add_piece_directional(desc)
                        elif piece_type == 'c':
                            self._add_piece_coordinate(desc)
                        elif piece_type == 't':
                            self._add_piece_tetromino(desc)
                        elif piece_type == 'p':
                            self._add_piece_pentomino(desc)
                        else:
                            raise Exception('Unknown piece type: %s' % piece_type)
            self._generate_mods()

    def _add_piece_directional(self, desc):
        """
        Adds a puzzle piece defined by a directional description to the puzzle
        """
        x, y = 0, 0
        path = [(x, y)]
        for c in desc:
            if c == 'n':
                y -= 1
                path.append((x, y))
            elif c == 's':
                y += 1
                path.append((x, y))
            elif c == 'w':
                x -= 1
                path.append((x, y))
            elif c == 'e':
                x += 1
                path.append((x, y))
        if len(path) == 1:
            raise Exception('Invalid directional description: %s' % desc)
        self.pieces.append(path)

    def _add_piece_coordinate(self, desc):
        """
        Adds a puzzle piece defined by a list of coordinates to the puzzle
        """
        path = []
        coords = desc.split(',')
        for i in range(len(coords) / 2):
            x, y = coords[2*i:2*i+2]
            path.append((int(x), int(y)))
        if len(path) < 1:
            raise Exception('Invalid coordinate description: %s' % desc)
        self.pieces.append(path)

    def _add_piece_tetromino(self, desc):
        """Adds a tetromino puzzle piece to the puzzle"""

        tetrominos = {
            'i':[(0, 0), (0, 1), (0, 2), (0, 3)],
            'j':[(0, 0), (0, 1), (0, 2), (-1, 2)],
            'l':[(0, 0), (0, 1), (0, 2), (1, 2)],
            't':[(0, 0), (0, 1), (0, 2), (1, 1)],
            's':[(0, 0), (0, 1), (1, 1), (1, 2)],
            'z':[(1, 0), (1, 1), (0, 1), (0, 2)],
            'o':[(0, 0), (1, 0), (0, 1), (1, 1)]
            }
        if desc in tetrominos:
            self.pieces.append(tetrominos[desc])
        else:
            raise Exception('Invalid tetromino: %s' % desc)

    def _add_piece_pentomino(self, desc):
        """Adds a pentomino puzzle piece to the puzzle"""

        pentominos = {
            'f' :[(0, 0), (1, 0), (0, 1), (-1, 1), (0, 2)],
            "f'":[(0, 0), (-1, 0), (0, 1), (1, 1), (0, 2)],
            'i' :[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
            'l' :[(0, 0), (0, 1), (0, 2), (0, 3), (1, 3)],
            "l'":[(0, 0), (0, 1), (0, 2), (0, 3), (-1, 3)],
            'n' :[(0, 0), (0, 1), (0, 2), (-1, 2), (-1, 3)],
            "n'":[(0, 0), (0, 1), (0, 2), (1, 2), (1, 3)],
            'p' :[(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)],
            "p'":[(0, 0), (-1, 0), (0, 1), (-1, 1), (0, 2)],
            't' :[(-1, 0), (0, 0), (1, 0), (0, 1), (0, 2)],
            'u' :[(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0)],
            'v' :[(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)],
            'w' :[(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)],
            'x' :[(0, 0), (0, 1), (-1, 1), (1, 1), (1, 2)],
            'y' :[(0, 0), (-1, 1), (0, 1), (0, 2), (0, 3)],
            "y'":[(0, 0), (1, 1), (0, 1), (0, 2), (0, 3)],
            'z' :[(-1, 0), (0, 0), (0, 1), (0, 2), (1, 2)],
            "z'":[(1, 0), (0, 0), (0, 1), (0, 2), (-1, 2)]
            }

        if desc in pentominos:
            self.pieces.append(pentominos[desc])
        else:
            raise Exception('Invalid pentomino: %s' % desc)

    def _generate_mods(self):
        """
        Generates all allowed rotations, reflections, and translations of all
        puzzle pieces
        """

        for piece in self.pieces:
            # Construct all possible rotations and reflections for the piece,
            # if allowed by the puzzle rules
            mods = [piece]
            if self.allow_rotations:
                for rot in range(1, 4):
                    mods.append(rotate_piece(piece, rot))
            if self.allow_reflections:
                reflected_piece = reflect_piece(piece)
                mods.append(reflected_piece)
                if self.allow_rotations:
                    for rot in range(1, 4):
                        mods.append(rotate_piece(reflected_piece, rot))
            mods = list(frozenset(map(frozenset, mods)))

            # Compute all possible valid translations of each rotation and
            # reflection
            all_trans = []
            for mod in mods:
                for y in range(self.height):
                    for x in range(self.width):
                        trans = translate_piece(mod, x, y)
                        if self._fits_in_grid(trans):
                            all_trans.append(frozenset(trans))
            self.piece_trans.append(all_trans)

    def _fits_in_grid(self, piece):
        """Tests if the given puzzle piece can be placed in our initial grid"""

        for x, y in piece:
            if x < 0 or y < 0 or x >= self.width or y >= self.height:
                return False
            if self.initial_grid[y][x]:
                return False
        return True

    def convert_to_sat(self):
        """Converts the polyomino puzzle into a SAT problem"""

        # For each position and orientation of each puzzle piece, we create a
        # boolean variable indicating if that piece can go there that way.

        # Number of pieces and number of variables for each piece
        N = len(self.pieces)
        self.num_trans = map(len, self.piece_trans)

        # Variable offsets within each piece, 1-indexed for easier conversion
        # to a problem description solvable by a SAT solver
        self.var_offsets = [sum(self.num_trans[:i]) + 1 for i in range(N+1)]
        self.sat_clauses = []

        # Create a clause saying that a piece can't go in two places at once
        for i in range(N):
            for j in range(self.num_trans[i]):
                for k in range(j+1, self.num_trans[i]):
                    self.sat_clauses.append((-(self.var_offsets[i] + j), -(self.var_offsets[i] + k)))

        # Create a clause saying that a piece has to go in at least one place
        for i in range(N):
            self.sat_clauses.append(range(self.var_offsets[i], self.var_offsets[i + 1]))

        # Create a clause saying two pieces can't go in incompatible locations
        for i in range(N):
            for j in range(i+1, N):
                for k in range(self.num_trans[i]):
                    for l in range(self.num_trans[j]):
                        if not self.piece_trans[i][k].isdisjoint(self.piece_trans[j][l]):
                            self.sat_clauses.append((-(self.var_offsets[i] + k), -(self.var_offsets[j] + l)))

    def solve_sat(self):
        """Solves the SAT problem generated by convert_to_sat()"""

        sat = subprocess.Popen(['glucose_static', '-verb=0', '-model'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        # Write out the SAT problem to the solver; note that this could
        # deadlock in theory, but we're assuming that the solver is
        # well-behaved and reads all of its input before it prints enough
        # output that would cause it to block there.
        sat_problem = 'p cnf %d %d\n' % (sum(self.num_trans), len(self.sat_clauses))
        for clause in self.sat_clauses:
            sat_problem += ' '.join(map(str, clause)) + ' 0\n'

        output = sat.communicate(sat_problem)[0]

        for line in output.splitlines(False):
            if line == 's UNSATISFIABLE':
                return []
            elif line[:2] == 'v ':
                # TODO: Multiple solutions?  glucose only gives one solution to
                # the SAT problem
                var_values = map(int, line.split()[1:])
                return [PolyominoSolution(self, var_values)]

        return []

class PolyominoSolution:
    """Class representing one solution to a polyomino puzzle"""
    def __init__(self, puzzle, var_values):
        self.puzzle = puzzle
        self.grid = [[1 if puzzle.initial_grid[y][x] else 0 for x in range(puzzle.width)] for y in range(puzzle.height)]

        # Convert the SAT solution into a grid of color indices
        all_piece_trans = reduce(operator.add, puzzle.piece_trans)
        next_color = 2
        for value in var_values:
            if value > 0:
                for x, y in all_piece_trans[value - 1]:
                    assert self.grid[y][x] == 0
                    self.grid[y][x] = next_color
                next_color += 1
        assert next_color == len(puzzle.pieces) + 2

        # Generate color palette
        self.palette = [(255, 255, 255), (0, 0, 0)]
        for i in range(2, next_color):
            self.palette.append((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    def render(self, filename):
        """Renders the puzzle solution to a PNM file"""

        SCALE = 21
        width = self.puzzle.width * SCALE + 1
        height = self.puzzle.height * SCALE + 1
        pixels = [[(0, 0, 0) for y in range(height)] for x in range(width)]

        # Scale up the solution, colorize according to the palette, and remove
        # edges between squares in the same piece
        for y in range(height):
            y2 = y / SCALE
            for x in range(width):
                x2 = x / SCALE
                if x % SCALE == 0:
                    if y % SCALE == 0:
                        pixels[y][x] = self.palette[1]
                    elif x > 0 and x < width - 1 and self.grid[y2][x2 - 1] == self.grid[y2][x2]:
                        pixels[y][x] = self.palette[self.grid[y2][x2]]
                    else:
                        pixels[y][x] = self.palette[1]
                elif y % SCALE == 0:
                    if y > 0 and y < height - 1 and self.grid[y2 - 1][x2] == self.grid[y2][x2]:
                        pixels[y][x] = self.palette[self.grid[y2][x2]]
                    else:
                        pixels[y][x] = self.palette[1]
                else:
                    pixels[y][x] = self.palette[self.grid[y2][x2]]

        # Write out the PNM file
        with open(filename, 'wb') as f:
            f.write('P6 %d %d\n255\n' % (width, height))
            for row in pixels:
                for pixel in row:
                    f.write(struct.pack('BBB', *pixel))

def rotate_piece(piece, rot):
    """Rotates a puzzle piece description by 0, 90, 180, or 270 degrees"""

    if rot == 0:
        return piece
    elif rot == 1:
        return [(-y, x) for x, y in piece]
    elif rot == 2:
        return [(-x, -y) for x, y in piece]
    elif rot == 3:
        return [(y, -x) for x, y in piece]
    else:
        raise Exception('Invalid rotation: %s' % rot)

def reflect_piece(piece):
    """Reflects a puzzle piece about the x=y line"""
    return [(y, x) for x, y in piece]

def translate_piece(piece, dx, dy):
    """Translates a puzzle piece"""
    return [(x + dx, y + dy) for x, y in piece]

def usage():
    sys.stderr.write('Usage: %s puzzle-file\n' % sys.argv[0])
    sys.exit(1)

def display_image(filename):
    subprocess.Popen(['display', filename])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()

    random.seed(1337)

    print 'Reading puzzle: %s' % sys.argv[1]
    puzzle = PolyominoPuzzle(sys.argv[1])
    print 'Converting to SAT...'
    puzzle.convert_to_sat()
    print 'Solving SAT (%d variables, %d clauses)...' % (puzzle.var_offsets[-1], len(puzzle.sat_clauses))
    solutions = puzzle.solve_sat()
    print 'Found %d solutions' % len(solutions)
    if solutions:
        base = os.path.splitext(sys.argv[1])[0] + '-soln-%02d.pnm'
        out_filenames = [base % i for i in range(len(solutions))]
        print 'Saving solutions to %s .. %s' % (out_filenames[0], out_filenames[-1])
        for i in range(len(solutions)):
            solutions[i].render(out_filenames[i])
        try:
            for filename in out_filenames:
                display_image(filename)
        except OSError:
            print "Unable to display solution images, 'display' command not found"
