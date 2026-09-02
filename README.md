# `official/regex` v1

Status: **`0.3.0` (Toka `1.0.0-rc.11` release candidate)**.

`official/regex` is Toka's official regular-expression package. Its package
identity and public import path are `official/regex`; its manifest short name
is `regex`.

## Design boundary

v1 is a byte-oriented **RE2 syntax profile**. Its matcher uses a Thompson-style
NFA, never recursive backtracking. Matching state is bounded by the compiled
pattern and worst-case work is `O(pattern_bytes * input_bytes)`, rather than
exponential work from adversarial input. Pattern compilation has a fixed size
limit; malformed or oversized patterns return structured errors containing the
first relevant byte position. v1 limits patterns to 4096 bytes and parenthesis
nesting to 128 levels.

The public API is:

```toka
import official/regex::{Regex, RegexOptions, RegexAnalysis, CompiledRegex, RegexError}

auto compiled = Regex::compile("ab+c")
if compiled.is_ok() {
    assert(compiled.unwrap().is_match("abbbc"))
}

// Compile with options (case folding, word boundary, full line anchor)
auto opts = RegexOptions(ignore_ascii_case = true, word_regexp = false, line_regexp = false)
auto opt_compiled = Regex::compile_with_options("fn\\s+[a-z_]+", opts)
if opt_compiled.is_ok() {
    auto plan = opt_compiled.unwrap()
    assert(plan.is_match("FN foo"))
    auto ana = plan.analysis()
    assert(!ana.can_match_empty())
    assert(ana.required_literal().is_some())
}
```

`Regex::compile` returns `Result<Regex, RegexError>`. `Regex::compile_with_options`
returns `Result<CompiledRegex, RegexError>`. `Regex::is_match` tests whether any
substring matches; `Regex::find` returns byte offsets for the first match; and
`Regex::find_all` returns all leftmost, non-overlapping matches. Empty matches
are reported once at each search boundary and then advance one byte, avoiding an
infinite scan. The API owns compiled pattern data and never returns a view into
a temporary input.

`Regex::captures` returns the whole match at index `0` followed by numbered
parenthesized groups. Every value is a byte-offset range; a group skipped by
the winning optional or alternation path is `None`. A repeated group retains
its last successful iteration, matching the usual RE2/Rust-regex convention.
Named groups use Rust-compatible `(?<name>...)` or `(?P<name>...)` syntax and
are read with `captures.name("name")`. Names are unique ASCII identifiers.
`Regex::split` returns owned fields and retains leading or trailing empty
fields. `Regex::replace_all` accepts literal template text plus `$$`, `$0`,
and numbered `$1` through `$99` capture references.

`RegexSet::compile` compiles several independent patterns. Its `is_match`
method reports whether any member matches, while `matches` returns the matching
pattern indexes in declaration order. It does not expose match offsets; callers
that need them should retain and query an individual `Regex`.

## Module layout

The public `official/regex` module remains the only consumer entry point.
Internally, `model` owns the NFA data shapes and options, `syntax` parses and
compiles a pattern while performing required-literal analysis, `automata` executes
a compiled program with word/line boundary assertions, `engine` owns the public
`Regex` and `CompiledRegex` methods, and `set` provides multi-pattern search.

## Release lineage

- `0.1.0`: Initial release under `tokalang/toka` mono-repo.
- `0.1.1`: First standalone package release.
- `0.2.0`: Immutable stable release.
- `0.3.0`: Upgraded to Toka `1.0.0-rc.11` ownership and borrowing model; added
  `RegexOptions(ignore_ascii_case, word_regexp, line_regexp)`, `RegexAnalysis`,
  and `CompiledRegex` with conservative required-literal prefilter extraction.

## v1 syntax profile

- literal bytes and escapes for metacharacters;
- `.` for one non-LF byte (no dotall flag in v1);
- concatenation, numbered grouping `(...)`, named grouping `(?<name>...)` or
  `(?P<name>...)`, and alternation `|`;
- postfix `*`, `+`, `?`, and counted repetitions `{m}`, `{m,}`, `{m,n}`;
- ASCII byte classes such as `[abc]`, `[a-z]`, and `[^0-9]`;
- `^` and `$` anchors, plus native `word_regexp` and `line_regexp` assertions.

## Explicit non-goals

Backreferences, look-around, recursive patterns, named replacement references,
and Unicode property classes are outside v1.

## Qualification

Run the qualification from this package root:

```text
TOKA_ROOT=/path/to/toka python3 tests/qualify_package.py
```
