# regular

Regular is a toy regular expression engine.

I wanted to understand how regular expressions worked, so I read [this](http://dpk.io/dregs/toydregs) and then started working on regular. :sunny: The approach is to use derivatives, as described in the article.

## Notes

Instead of using normal syntax, I came up with something I liked:

    abc : Standard string, matches "abc" (and also "abcd" because partial matches count)
    |[a,b,c]| : Alternation of regexes.
    *(abc) : Matches the enclosed regex zero or more times
    _ : Matches any character

For example, `ap|[e,ple]|` would match `ape*` and `apple*`. It's not super polished -- none of the special characters can be escaped to be matched, for example, but otherwise supports everything expected (including nested expressions like `a|[b, |[c, d]|, e, f]|`).

## Usage

repl:

    python3 regular.py

Batch mode:

    python3 regular.py filename

In both modes, the input format is

    regex : test

## LICENSE

MIT, see [LICENSE](https://github.com/mtn/regular/blob/master/LICENSE)
