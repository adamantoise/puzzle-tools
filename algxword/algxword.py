#!/usr/bin/python

"""
Copyright (c) 2011, Adam Rosenfield
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

import sys

def usage(status):
    print """Usage: %s [OPTIONS...] WORDLIST FROM TO

Finds all words in the file WORDLIST (which need not be sorted) which would
continue to be words when substituting the substring FROM for the substring TO.
Only words which contain FROM in them are considered.

Both FROM and TO can be empty strings.  If FROM is the empty string, then TO is
added at each position in the string to test for a word.  If TO is the empty
string, then the FROM string is simply deleted.

Ordinarily, only the first occurrence of FROM is replaced with TO.  If the -a
option is specified, then all occurrences of FROM are replaced with TO.

OPTIONS:

-a      Replaces all occurrences of FROM with TO when testing for a word
--help  Prints this help message
""" % sys.argv[0]
    sys.exit(status)

max_replace = 1

while len(sys.argv) > 1:
    if sys.argv[1][0] == '-':
        opt = sys.argv[1]
        del sys.argv[1]
        if opt == '-a':
            max_replace = 99999;
        elif opt == '--help':
            usage(0)
        elif opt == '--':
            break
        else:
            print 'Unrecognized option: %s' % opt
            usage(1)
    else:
        break

if len(sys.argv) < 4:
    usage(1)

pattern = sys.argv[2]
repl = sys.argv[3]

with open(sys.argv[1]) as dictfile:
    wordlist = [word.strip() for word in dictfile]

wordset = frozenset(wordlist)

count = 0

try:
    if pattern:
        for word in wordlist:
            if word.find(pattern) != -1:
                r = word.replace(pattern, repl, max_replace)
                if r in wordset:
                    print '%s ==> %s' % (word, r)
                    count += 1
                    if count % 24 == 0:
                        sys.stdout.flush()
    else:
        # Special case the empty pattern to avoid an extra branch in the inner
        # loop
        for word in wordlist:
            for i in range(len(word) + 1):
                r = word[:i] + repl + word[i:]
                if r in wordset:
                    print '%s ==> %s' % (word, r)
                    count += 1
                    if count % 24 == 0:
                        sys.stdout.flush()
finally:
    # In case user Ctrl+C's us
    sys.stdout.flush()
