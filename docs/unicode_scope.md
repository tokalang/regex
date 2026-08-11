# Unicode regex scope

## Decision

`0.2.0` remains byte-oriented. Its `Regex`, `Match`, `Captures`, `split`, and
`replace_all` APIs keep byte offsets and the current ASCII meaning of `.`,
character classes, and shorthand classes.

Unicode support will be a later, opt-in `UnicodeRegex` API rather than a
silent semantic change to `Regex`. A match from either API continues to report
UTF-8 byte offsets, so callers can use one offset representation across the
package.

This is intentionally not grapheme matching. A Unicode regex atom consumes
one Unicode scalar value; user-perceived grapheme clusters remain the concern
of `official/unicode`.

## First implementation slice

The first Unicode slice is contingent on a released `official/unicode` package
that exposes locked Unicode data. It will add:

- UTF-8 scalar literals and `.` matching one scalar except LF;
- scalar character ranges such as `[α-ω]`;
- Unicode general-category and script properties with `\p{...}` and
  `\P{...}`;
- Unicode meanings for `\d`, `\w`, and `\s`, while preserving the existing
  byte API unchanged;
- explicit malformed-UTF-8 errors from Unicode matching operations.

Named captures, split, and replacement will be layered on the Unicode engine
only after scalar matching and properties qualify. Capture offsets stay in
bytes; replacement text is copied as UTF-8 byte ranges after validation.

## Deliberate exclusions

The first slice does not include normalization, canonical-equivalence matching,
case folding flags, grapheme-cluster atoms, word-boundary Unicode algorithms,
look-around, or backreferences. These each need independent semantics and
resource analysis.

## Data and release rule

The implementation must depend on the released `official/unicode` package;
it must not copy generated tables, download UCD data during a consumer build,
or rely on ICU, CoreFoundation, or host Unicode data. The dependency version,
Unicode version, and source checksums become part of the regex release record.

At the time of this document, the local Toka source contains a qualified
Unicode 17.0.0 grapheme package, but it is not a registry release. Unicode
regex work therefore begins only after that package has a stable registry
identity and an offline consumer replay.

## Acceptance gates

1. Keep existing byte `Regex` qualification unchanged.
2. Add scalar-boundary tests for two-, three-, and four-byte UTF-8 sequences.
3. Generate property tests from the locked UCD version, including positive and
   negative property examples and boundary ranges.
4. Verify malformed UTF-8 returns a structured error without partial matching.
5. Preserve bounded Thompson-NFA execution and extend the benchmark with
   scalar/property workloads before enabling the API in a registry release.
