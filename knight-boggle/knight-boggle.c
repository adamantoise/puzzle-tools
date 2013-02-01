// Copyright (C) 2013 Adam Rosenfield
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to
// deal in the Software without restriction, including without limitation the
// rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
// sell copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
// IN THE SOFTWARE.

// This program finds words hidden Boggle-style in a grid with the variant that
// words are to spelled by making knight's moves instead of the 8 cardinal
// directions.  It was originally written to solve Matt Gaffney's Weekly
// Crossword Contest #243 "Knight Moves", available here:
// http://xwordcontest.com/2013/01/mgwcc-243-friday-january-25th-2013-knight-moves.html

// Although the grid and start locations for the puzzle are hard-coded, it
// should be trivial to modify to any arbitrary grid.  Likewise, if you want
// to solve a regular Boggle puzzle, that's also a trivial modification.

#include <ctype.h>
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Size of the grid (assumed to be square)
#define N 15

#define DIM(x) (sizeof(x)/sizeof(*(x)))

// Grid to search for words in
const char grid[N][N+1] = {
  "par...twa.aesir",
  "stop.goal.quote",
  "40yearoldvirgin",
  "...ski.kai.yost",
  ".spcas...eid...",
  "thai.screwrings",
  "har..oral.scena",
  "east.momsa.etal",
  "dream.wail..hrs",
  "jackdaniel.bela",
  "...ecu...garry.",
  "shin.era.ida...",
  "centerofgravity",
  "orsew.mail.oreo",
  "tatas.erg...ken"
};

// (row, column) starting locations to search for words from
const int startLocs[6][2] = {
  {2, 11},
  {2, 14},
  {5, 3},
  {5, 12},
  {12, 2},
  {13, 8}
};

// Node in a trie, used for storing our word list
typedef struct Node
{
  bool isword;
  struct Node *children[26];
} Node;

// Allocates and initializes a leaf node of the trie
Node *make_node()
{
  return calloc(1, sizeof(Node));
}

// Frees a trie node and all its children
void free_node(Node *node)
{
  if(node == NULL)
    return;
  
  for (int i = 0; i < 26; i++)
    free_node(node->children[i]);

  free(node);
}

// Adds a word to a trie
void add_word(Node *node, const char *word)
{
  if (*word == 0 || *word == '\n')
    node->isword = true;
  else
  {
    int i = tolower(*word);
    if (i < 'a' || i > 'z')
      return;
    i -= 'a';
    if (node->children[i] == NULL)
      node->children[i] = make_node();
    add_word(node->children[i], word + 1);
  }
}

// Searches for words in the grid Boggle-style using knights moves
void search(int r, int c, Node *node, char *word, int depth, bool visited[N][N])
{
  // Our 8 possible moves -- modify this to use other movement types
  static const int kDeltas[8][2] = {
    {2, 1},
    {1, 2},
    {-1, 2},
    {-2, 1},
    {-2, -1},
    {-1, -2},
    {1, -2},
    {2, -1}
  };

  word[depth] = grid[r][c];
  visited[r][c] = true;

  // Print out all words found >= 6 letters in length (we have a length-1
  // word at depth 0)
  if (depth >= 5 && node->isword)
  {
    word[depth + 1] = 0;
    printf("%s\n", word);
  }

  for (int i = 0; i < 8; i++)
  {
    int r2 = r + kDeltas[i][0];
    int c2 = c + kDeltas[i][1];
    if (r2 >= 0 && r2 < N && c2 >= 0 && c2 < N && !visited[r2][c2])
    {
      int ch = grid[r2][c2];
      if (ch != '.')
      {
        Node *child = node->children[ch - 'a'];
        if (child != NULL)
        {
          search(r2, c2, child, word, depth + 1, visited);
        }
      }
    }
  }

  visited[r][c] = false;
}

int main(int argc, char **argv)
{
  // First and only argument is the filename of the word list to use for our
  // dictionary
  if (argc != 2)
  {
    fprintf(stderr, "Usage: %s wordlist\n", argv[0]);
    return 1;
  }

  FILE *f = fopen(argv[1], "r");
  if (f == NULL)
  {
    fprintf(stderr, "%s: %s\n", argv[1], strerror(errno));
    return 1;
  }

  Node *root = make_node();

  // Read in each word in the word list and add it to our trie
  char word[255];
  while (fgets(word, DIM(word), f))
  {
    add_word(root, word);
  }
  
  fclose(f);
  printf("[finished reading world list]\n");

  // Search for words starting at each start location
  for (int i = 0; i < DIM(startLocs); i++)
  {
    word[0] = 0;
    bool visited[N][N] = {{0}};
    int r = startLocs[i][0];
    int c = startLocs[i][1];
    int ch = grid[r][c];
    search(r, c, root->children[ch - 'a'], word, 0, visited);
    printf("\n");
  }

  // We could free the trie here, but doing so node-by-node is very slow.  We
  // could instead use a pool allocator for the nodes and free the entire pool
  // at once, but there's not much point in doing that for such a simple
  // program as this.  Instead, we just leak the memory and let the OS clean
  // up after us, which is very fast.
  
  //free_node(root);
  
  return 0;
}
