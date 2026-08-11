# `official/regex` 0.2 release gate

`0.2.0-dev.0` contains the candidate API: byte-oriented bounded matching,
`RegexSet`, numbered and named captures, `split`, and numbered capture
replacement templates. No new public API is added after this gate without
starting the next minor line.

Before publishing `0.2.0`:

1. Run `TOKA_ROOT=/path/to/toka python3 tests/qualify_package.py` from a clean
   checkout on Linux x64 and macOS arm64. Record the exact source commit.
2. Run `TOKA_ROOT=/path/to/toka python3 bench/run_bench.py` and retain the
   result as a regression baseline, not a cross-machine performance target.
3. Change `package.tk` from `0.2.0-dev.0` to the final immutable `0.2.0`, then
   re-run qualification. Do not republish or alter `0.1.1`.
4. Create annotated tag `v0.2.0` at that qualified commit and attach the
   deterministic `regex-0.2.0.tar.gz` archive to its GitHub Release.
5. Calculate the archive SHA-256 and package-content digest; submit the
   approved static catalog change for `pkg.tokalang.dev`. The catalog entry
   must name the tag, release asset URL, and both immutable digests.
6. In a fresh consumer using the default registry, resolve exact `0.2.0`,
   commit the generated lock, and prove `TOKA_OFFLINE=1 toka fetch/build/run`
   replays it unchanged.

Publication needs repository and catalog authority. `toka publish` may create
the archive but does not replace the tagged-release plus reviewed-catalog step.
