---
id: M3-HER-1130
title: "Tests that leave nodes in the scene tree (the runner frees and reports them; owners free their own)"
role: qa
status: doing
owner_session: "integration-qa (hero-integration track, session_01PzF7Jc4XVQdTWcaYUyCjPB)"
reviewer: lead
depends_on: []
milestone: M3
request-from: lead
---
## Goal
A test that leaves a node under the current scene can break every later test. One field zone left by
test_hero_stairs failed ~30 tests in big13. Since c895c542+ the runner frees whatever a test leaves there and prints a
`LEAK <file>::<test>: ...` line. The summary reads "Tests: N run, M failed, K left nodes in the tree". It reports and
doesn't fail yet, so no track's suite goes red overnight.

## Acceptance criteria
- [ ] The full list of leaking tests, by owner, with a request to each owner (each test frees what it and its
      before_each add, or queue_frees it).
- [ ] When the list is empty, the runner fails a leak (one line in tests/run_tests.gd), so none come back.

## Review log
