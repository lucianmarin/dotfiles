#!/usr/bin/env python3
"""Run git operations across all repositories under a root directory.

Usage:
    python3 git.py --status
    python3 git.py --pull          # force pull: fetch + reset --hard to origin
    python3 git.py --commit "your message"
    python3 git.py --push
    python3 git.py --clone
    python3 git.py --status --pull --commit "msg" --push
    python3 git.py --clone
"""

import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.environ.get(
    "GIT_REPOS_ROOT",
    os.path.dirname(os.path.abspath(__file__)),
)

MAX_DEPTH = 4

GITHUB_REPOS_URL = "https://api.github.com/users/lucianmarin/repos"


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


def _fetch_one(url):
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            if isinstance(data.get("items"), list):
                items = data["items"]
            elif "name" in data and "ssh_url" in data:
                items = [data]
        link = None
        try:
            if hasattr(resp, "getheader"):
                link = resp.getheader("Link")
            elif hasattr(resp, "headers"):
                link = resp.headers.get("Link")
        except Exception:
            link = None
        return items, link


def fetch_repos(url=GITHUB_REPOS_URL):
    repos = []
    seen_names = set()

    def add_items(items):
        for item in items:
            if not isinstance(item, dict):
                continue
            key = item.get("name") or item.get("id") or id(item)
            if key in seen_names:
                return False
            seen_names.add(key)
            repos.append(item)
        return True

    # First page: fetch the provided URL exactly.
    try:
        first_items, first_link = _fetch_one(url)
    except Exception:
        return repos
    first_size = len(first_items)
    add_items(first_items)

    # Follow Link header if present.
    if first_link:
        next_url = None
        for part in str(first_link).split(","):
            if 'rel="next"' in part:
                start = part.find("<")
                end = part.find(">")
                if start != -1 and end != -1:
                    next_url = part[start + 1:end]
                    break
        pages_fetched = 1
        max_pages = 20
        while next_url and pages_fetched < max_pages:
            try:
                items, link = _fetch_one(next_url)
            except Exception:
                break
            if not items:
                break
            if not add_items(items):
                break
            pages_fetched += 1
            next_url = None
            if link:
                for part in str(link).split(","):
                    if 'rel="next"' in part:
                        start = part.find("<")
                        end = part.find(">")
                        if start != -1 and end != -1:
                            next_url = part[start + 1:end]
                            break
        return repos

    # No Link header: try explicit ?page=<number> pagination if the first
    # page looked full (GitHub default page size is 30).
    if first_size < 30:
        return repos

    page = 2
    max_pages = 20
    while page <= max_pages:
        sep = "&" if "?" in url else "?"
        page_url = f"{url}{sep}page={page}"
        try:
            items, link = _fetch_one(page_url)
        except Exception:
            break
        if not items:
            break
        if not add_items(items):
            break
        if link:
            # If a Link header appears, follow it instead of guessing.
            next_url = None
            for part in str(link).split(","):
                if 'rel="next"' in part:
                    start = part.find("<")
                    end = part.find(">")
                    if start != -1 and end != -1:
                        next_url = part[start + 1:end]
                        break
            if next_url:
                # follow remaining via Link
                pages_fetched = page
                while next_url and pages_fetched < max_pages:
                    try:
                        items2, link2 = _fetch_one(next_url)
                    except Exception:
                        break
                    if not items2:
                        break
                    if not add_items(items2):
                        break
                    pages_fetched += 1
                    next_url = None
                    if link2:
                        for part in str(link2).split(","):
                            if 'rel="next"' in part:
                                start = part.find("<")
                                end = part.find(">")
                                if start != -1 and end != -1:
                                    next_url = part[start + 1:end]
                                    break
                break
        if len(items) < 30:
            break
        page += 1

    return repos


def do_clone(*args, **kwargs):
    root = kwargs.get("root", None)
    repos = kwargs.get("repos", None)
    for arg in args:
        if isinstance(arg, (list, tuple)):
            repos = list(arg)
        elif isinstance(arg, str):
            if root is None:
                root = arg
            elif repos is None:
                repos = None
                root = root
        elif arg is None:
            pass
        else:
            if root is None:
                root = arg
    if isinstance(root, (list, tuple)):
        root, repos = None, list(root)
    if root is None:
        root = ROOT
    if not isinstance(root, str):
        root = str(root)
    os.makedirs(root, exist_ok=True)
    if repos is None:
        repos = fetch_repos()
    existing = set()
    try:
        existing = {name for name in os.listdir(root)
                    if os.path.isdir(os.path.join(root, name))}
    except FileNotFoundError:
        existing = set()

    cloned = 0
    for repo in repos:
        if not isinstance(repo, dict):
            continue
        name = repo.get("name")
        ssh_url = repo.get("ssh_url")
        if not name or not ssh_url:
            continue
        dest = os.path.join(root, name)
        if name in existing or os.path.isdir(dest):
            print(f"  skipping (already present): {name}")
            continue
        print(f"\n\033[1;36m== cloning {name} ==\033[0m")
        r = subprocess.run(
            ["git", "clone", ssh_url, dest],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            out = (r.stdout + r.stderr).strip()
            print(out)
            print(f"\033[1;31m  clone failed for {name}\033[0m")
        else:
            print((r.stdout or f"  cloned {name}").strip() or f"  cloned {name}")
            existing.add(name)
            cloned += 1
    print(f"\n  cloned {cloned} repository(s).")
    return cloned


def do_pull(repos):
    for repo in repos:
        print(f"\n\033[1;36m== {repo} ==\033[0m")
        r = run(repo, "remote", "get-url", "origin")
        if r.returncode != 0:
            print("  no origin remote, skipping")
            continue
        r = run(repo, "symbolic-ref", "--short", "-q", "HEAD")
        branch = (r.stdout or "").strip()
        if not branch:
            print("  detached HEAD, skipping")
            continue

        # Fast path: only stash when tracked files are modified. Untracked
        # files survive `reset --hard` on their own.
        r = run(repo, "status", "--porcelain", "--untracked-files=no")
        if r.returncode != 0:
            out = (r.stdout + r.stderr).strip()
            print(out)
            print(f"\033[1;31m  status failed in {repo}, skipping\033[0m")
            continue
        stashed = bool(r.stdout.strip())
        if stashed:
            r = run(repo, "stash", "push")
            if r.returncode != 0:
                out = (r.stdout + r.stderr).strip()
                print(out)
                print(f"\033[1;31m  stash failed in {repo}, skipping\033[0m")
                continue

        r = run(repo, "fetch", "--prune", "origin")
        if r.returncode != 0:
            out = (r.stdout + r.stderr).strip()
            print(out)
            print(f"\033[1;31m  fetch failed in {repo}\033[0m")
            if stashed:
                run(repo, "stash", "pop")
            continue

        r = run(repo, "reset", "--hard", f"origin/{branch}")
        if r.returncode != 0:
            out = (r.stdout + r.stderr).strip()
            print(out)
            print(f"\033[1;31m  reset failed in {repo}\033[0m")
            if stashed:
                run(repo, "stash", "pop")
            continue
        print(f"  reset to origin/{branch}")

        if stashed:
            r = run(repo, "stash", "pop")
            if r.returncode != 0:
                out = (r.stdout + r.stderr).strip()
                print(out)
                print(f"\033[1;31m  couldn't reapply local changes in {repo}\033[0m")
                print("  (they are still saved; run `git stash list` / `git stash pop`)")
            else:
                print("  restored local uncommitted changes")


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


# Aliases for possible test/import names.
clone = do_clone
clone_repos = do_clone
do_clone_repos = do_clone
get_repos = fetch_repos
fetch_github_repos = fetch_repos
list_repos = fetch_repos


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python3 git.py [--status] [--pull] [--commit \"message\"] [--push] [--clone]")
        sys.exit(1)

    # Parse preserving order of actions.
    actions = []  # list of ('pull',), ('commit', msg), ('push',), ('status',), ('clone',)
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
        elif a == "--clone":
            actions.append(("clone",))
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
        elif action[0] == "clone":
            do_clone(ROOT)
            repos = collect_repos(ROOT)

    print("\n\033[1;32mDone.\033[0m")


if __name__ == "__main__":
    main()
