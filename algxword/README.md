# About

This program is a tool for crossword puzzle constructors, to help find words that become other words when a substring is added and/or removed.  It can be used to find theme answers for so-called "[algebraic crosswords](http://www.crosswordfiend.com/blog/2011/04/23/algebraic-crosswords-cts-10/)".

It is a command line utility written in Python 2.x.  If your system already has Python installed (such as Linux or Mac OS X), it can be ran out-of-the-box.  If you do not have Python installed, Python can be obtained [here](http://python.org/download/).  Make sure to download a version 2.x release, as this program is not compatible with version 3.x (though it can be made compatible with some trivial changes to the source code or with the `2to3` utility).

This program also requires a user-supplied word list.  Most Linux and OS X systems ship with a reasonable word list located at `/usr/share/dict/words`.  The word list should contain one word per line, but it need not be sorted.

# Usage

First, open up a terminal window:

- On Windows, open up `Start > Run` (or press <kbd>Win+R</kbd>) and type `cmd`
- On Mac OS X, open up `Applications/Utilities/Terminal.app`
- If you're running another operating system, you should be smart enough to figure out how to open up a terminal

Invoke the program as follows:

    python algxword.py [optional arguments] WORDLIST FROM TO

where `WORDLIST` is the filename of the word list you wish to use, `FROM` is the search pattern you wish to replace, and `TO` is the pattern you wish to replace it with.

This will find all words in the file `WORDLIST` which would continue to be words when substituting the substring `FROM` for the substring `TO`.  Only words which contain `FROM` in them are considered.

Both `FROM` and `TO` can be empty strings (which should be typed on the command line as an empty pair of quotes like `""`).  If `FROM` is the empty string, then `TO` is added at each position in the string to test for a word.  If `TO` is the empty string, then the `FROM` string is simply deleted.

Ordinarily, only the first occurrence of `FROM` is replaced with `TO`.  If the `-a` option is specified, then all occurrences of `FROM` are replaced with `TO`.

The `--help` option can also be specified to print out this usage information.

# Examples

Find all words which remain words when substituting the first occurrence of
`qu` for `k` in the word list `/usr/share/dict/words`:

    python algxword.py /usr/share/dict/words qu k

Same as above, but replace all occurrences of `qu` for `k`

    python algxword.py -a /usr/share/dict/words qu k

Find all words which can have an `lax` inserted in them

    python algxword.py /usr/share/dict/words "" lax
