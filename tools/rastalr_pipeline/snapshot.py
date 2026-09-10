"""Protect historical hashes while permitting only named new reference trees."""
from pathlib import PurePosixPath


def compare_snapshots(baseline, current, *, allowed_addition_prefixes=()):
    """Never exempt an existing baseline file, even inside an allowed tree.

    Snapshots must be obtained by reading current files, not by updating baseline
    values. Missing files, byte changes, count changes and unlisted additions fail.
    """
    old, new = baseline["sha256"], current["sha256"]
    missing = sorted(set(old) - set(new))
    changed = sorted(path for path in old.keys() & new.keys() if old[path] != new[path])
    additions = sorted(set(new) - set(old))

    def allowed(path):
        relative = PurePosixPath(path)
        return (not relative.is_absolute() and ".." not in relative.parts
                and any(relative.is_relative_to(PurePosixPath(prefix))
                        for prefix in allowed_addition_prefixes))

    unexpected = [path for path in additions if not allowed(path)]
    counts_match = baseline["counts"] == current["counts"]
    return {
        "expected_counts": baseline["counts"], "observed_counts": current["counts"],
        "protected_file_count": len(old), "missing": missing, "changed": changed,
        "authorized_additions": [path for path in additions if allowed(path)],
        "unauthorized_additions": unexpected,
        "method": "Compare existence and SHA-256 of every historical file; allow only new files under explicitly named paths",
        "pass": counts_match and not missing and not changed and not unexpected,
    }
