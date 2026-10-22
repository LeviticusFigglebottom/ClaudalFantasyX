"""Deterministic parallel rendering of independent notes.

Each job is (callable, kwargs). Results come back in submission order and
each job seeds its own generator, so the output does not depend on how the
work was split across processes. HYMN_AUDIO_JOBS=1 forces serial rendering.
"""
from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor


def _call(job):
    fn, kw = job
    return fn(**kw)


def render_jobs(jobs: list, workers: int | None = None) -> list:
    workers = workers or int(os.environ.get("HYMN_AUDIO_JOBS", "0")) or (os.cpu_count() or 1)
    if workers <= 1 or len(jobs) < 8:
        return [_call(j) for j in jobs]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(_call, jobs, chunksize=max(1, len(jobs) // (workers * 8))))
