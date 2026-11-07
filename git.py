#!/usr/bin/env python3
"""Run git operations across all repositories under a root directory.

Usage:
    python3 git.py --status
    python3 git.py --pull
    python3 git.py --commit "your message"
    python3 git.py --push
    python3 git.py --status --pull --commit "msg" --push
"""

import os
import subprocess
import sys

ROOT = os.environ.get(
    "GIT_REPOS_ROOT",
    os.path.dirname(os.path.abspath(__file__)),
)

MAX_DEPTH = 4


def collect_repos(root):
    repos = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if depth > MAX_DEPTH:
            dirnames[:] = []
            continue
        if ".git" in dirnames or ".git" in filenames:
            repos.append(dirpath)
            # don't descend into a repo's internals
            dirnames[:] = [d for d in dirnames if d != ".git"]
    repos.sort()
    return repos


def run(repo, *args):
    return subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True,
        text=True,
    )


def do_pull(repos):
    for repo in repos:
        print(f"\n\033[1;36m== {repo} ==\033[0m")
        r = run(repo, "pull", "--ff-only")
        if r.returncode != 0:
            out = (r.stdout + r.stderr).strip()
            print(out)
            print(f"\033[1;31m  pull failed in {repo}\033[0m")
        else:
            print((r.stdout or "  Already up to date.").strip())


def do_commit(repos, msg):
    for repo in repos:
        print(f"\n\033[1;36m== {repo} ==\033[0m")
        # check for changes
        r1 = run(repo, "diff", "--quiet")
        r2 = run(repo, "diff", "--cached", "--quiet")
        r3 = run(repo, "ls-files", "--others", "--exclude-standard")
        if r1.returncode == 0 and r2.returncode == 0 and not r3.stdout.strip():
            print("  nothing to commit")
            continue
        run(repo, "add", "-A")
        r = run(repo, "commit", "-m", msg)
        if r.returncode != 0:
            out = (r.stdout + r.stderr).strip()
            print(out)
            print(f"\033[1;31m  commit failed (or nothing to commit) in {repo}\033[0m")
        else:
            print(f"  committed: {msg}")


def do_status(repos):
    for repo in repos:
        print(f"\n\033[1;36m== {repo} ==\033[0m")
        r = run(repo, "status", "--short", "--branch")
        out = (r.stdout or "").strip()
        if not out:
            print("  (clean)")
        else:
            print(out)


def do_push(repos):
    for repo in repos:
        print(f"\n\033[1;36m== {repo} ==\033[0m")
        r = run(repo, "remote", "get-url", "origin")
        if r.returncode != 0:
            print("  no origin remote, skipping")
            continue
        r = run(repo, "push")
        if r.returncode != 0:
            out = (r.stdout + r.stderr).strip()
            print(out)
            print(f"\033[1;31m  push failed in {repo}\033[0m")
        else:
            print((r.stdout or "  pushed").strip() or "  pushed")


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python3 git.py [--status] [--pull] [--commit \"message\"] [--push]")
        sys.exit(1)

    # Parse preserving order of actions.
    actions = []  # list of ('pull',), ('commit', msg), ('push',)
    commit_msg = None
    i = 0
    n = len(args)
    while i < n:
        a = args[i]
        if a == "--pull":
            actions.append(("pull",))
        elif a == "--status":
            actions.append(("status",))
        elif a == "--push":
            actions.append(("push",))
        elif a == "--commit":
            i += 1
            if i >= n:
                print("Error: --commit requires a message argument.", file=sys.stderr)
                sys.exit(1)
            commit_msg = args[i]
            actions.append(("commit", commit_msg))
        elif a.startswith("--commit="):
            commit_msg = a[len("--commit="):]
            actions.append(("commit", commit_msg))
        else:
            print(f"Unknown option: {a}", file=sys.stderr)
            sys.exit(1)
        i += 1

    repos = collect_repos(ROOT)
    for action in actions:
        if action[0] == "status":
            do_status(repos)
        elif action[0] == "pull":
            do_pull(repos)
        elif action[0] == "commit":
            do_commit(repos, action[1])
        elif action[0] == "push":
            do_push(repos)

    print("\n\033[1;32mDone.\033[0m")


if __name__ == "__main__":
    main()
