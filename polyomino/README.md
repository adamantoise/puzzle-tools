# Polyomino solver

This is a script for solving [polyomino](http://en.wikipedia.org/wiki/Polyomino)-fitting problems, such as the puzzle ["Caterpillars"](http://web.mit.edu/puzzle/www/12/puzzles/betsy_johnson/caterpillars/) from the 2012 MIT Mystery Hunt.  In fact, it was written during the aforementioned Hunt for the purpose of solving the aforementioned puzzle, and then it was later polished up.

A polyomino-fitting puzzle is a puzzle where you have a set of polyominos and a grid you want to fill with them in a non-overlapping fashion.  The goal is to find if (a) there exists a valid placement of the polyominos and (b) one such placement.

The script works by converting the puzzle into a [SAT problem](http://en.wikipedia.org/wiki/Boolean_satisfiability_problem) and then feeding that into a SAT solver.

# Usage

First, download and compile [Glucose](http://www.lri.fr/~simon/?page=glucose), or another SAT solver.  If you use a different SAT solver, then you'll also need to change the reference to the `glucose` program in the source code; in theory, it should work with any SAT solver that can read problems expressed in the DIMACS format for CNF.

Add the path to `glucose` to your `$PATH` environment variable, and solve like so:

    python polyomino.py puzzle-file

If the puzzle is solved, a visual solution is written out into a NetPBM image (.pnm file).  If the `display(1)` program is in your `$PATH` (available via ImageMagick/GraphicsMagick), then the image will also be displayed automatically.  Otherwise, open it up yourself or convert it to a more useful format like PNG using any number of tools.

# Puzzle format

Puzzles are specified using a simple text format designed to be quick to type in.

Lines beginning with a hash mark (`#`) are comments which are ignored.

The first non-empty non-comment line should be either `rect <WIDTH> <HEIGHT>` or `custom <WIDTH> <HEIGHT>`:
- The `rect` type indicates that the grid into which the polyominos should be fitted is an empty rectangular grid of that size.
- The `custom` type indicates that the grid is non-empty subset of a rectangle.  Use this if you're fitting polyominos into an already partially-filled grid etc.  The grid is described by a `WIDTH*HEIGHT` array of 0's and 1's, where 0's indicate empty cells where polyominos can be placed, and 1's indicate filled cells where they cannot be placed.  For example, a puzzle with a diamond-shaped grid might be specified like this:
<pre>custom 7 7
1110111
1100011
1000001
0000000
1000001
1100011
1110111</pre>

After the grid come optional tokens indicating if the polyominos are allowed to be rotated and/or reflected.  By default, the can be rotated but not reflected.  The `no_rotations` keyword indicates that the polyminos can not be rotated, and the `allow_reflections` keyword indicates that they can be reflected.

Finally, the polyomino specifications follow.  Each subsequent non-empty, non-comment line defines one polyomino, which come in 4 flavors:
- Directional: `d` followed by a sequence of `n`, `e`, `s`, and `w` tokens, which describes a polyomino formed by beginning at an arbitrary point and walking in the given directions in order.  An L tetromino could be described by `d nne`.
- Tetromino: `t` followed by one of `i`, `j`, `l`, `t`, `s`, `z`, or `o`, which describes one of the 7 standard [tetrominos](http://en.wikipedia.org/wiki/Tetromino)
- Pentomino: `p` followed by one of `f`, `f'`, `i`, `l`, `l'`, `n`, `n'`, `p`, `p'`, `t`, `u`, `v`, `w`, `x`, `y`, `y'`, `z`, or `z'`, which describes one of the 12 standard [pentominos](http://en.wikipedia.org/wiki/Pentomino); the prime (`'`) variants are reflections.
- Coordinate: `c` followed by a comma-separated list of coordinate pairs of squares in the polyomino, e.g. `c 0,0, 1,0, 0,1, -1,0, 0,-1` describes the X pentomino.

For some sample puzzle files, see the files in the `puzzles/` subdirectory.
