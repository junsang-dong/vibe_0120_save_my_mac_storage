#!/usr/bin/env python3
#맥 스토리지에 쌓인 불필요한 파일을 확인하고 삭제하는 파이썬 프로그램
import argparse
import os
import shlex
import subprocess
import sys
from typing import List


def run_cmd(cmd: List[str], apply: bool) -> int:
    printable = " ".join(shlex.quote(c) for c in cmd)
    if not apply:
        print(f"[dry-run] {printable}")
        return 0
    print(f"[run] {printable}")
    return subprocess.call(cmd)


def rm_glob(path_glob: str, apply: bool) -> int:
    # Use /bin/rm -rf on known-safe paths only
    cmd = ["/bin/rm", "-rf", path_glob]
    return run_cmd(cmd, apply)


def du_sort(path: str) -> int:
    # du -xhd 1 PATH | sort -h
    du = subprocess.Popen(["/usr/bin/du", "-xhd", "1", path], stdout=subprocess.PIPE)
    sort = subprocess.Popen(["/usr/bin/sort", "-h"], stdin=du.stdout)
    if du.stdout:
        du.stdout.close()
    return sort.wait()


def diagnose() -> int:
    print("== Diagnose: large folders ==")
    du_sort(os.path.expanduser("~"))
    du_sort(os.path.expanduser("~/Library"))
    du_sort(os.path.expanduser("~/Library/Application Support"))
    du_sort(os.path.expanduser("~/Library/Containers"))
    return 0


def safe_clean(apply: bool) -> int:
    print("== Safe cache/log cleanup ==")
    cmds = [
        "~/Library/Caches/*",
        "~/Library/Logs/*",
        "~/Library/Application Support/CrashReporter/*",
        "~/Library/Application Support/CloudDocs/session/*",
    ]
    for p in cmds:
        rm_glob(os.path.expanduser(p), apply)

    # System caches/logs (requires sudo externally if needed)
    rm_glob("/Library/Caches/*", apply)
    rm_glob("/Library/Logs/*", apply)
    return 0


def dev_clean(apply: bool) -> int:
    print("== Dev cache cleanup ==")
    targets = [
        "~/Library/Developer/Xcode/DerivedData/*",
        "~/Library/Developer/Xcode/Archives/*",
        "~/Library/Developer/CoreSimulator/Caches/*",
        "~/Library/Caches/CocoaPods/*",
        "~/.cocoapods/repos/*",
        "~/Library/Caches/Homebrew/*",
        "~/.npm/_cacache/*",
        "~/.yarn/cache/*",
        "~/Library/Caches/pip/*",
        "~/.gradle/caches/*",
        "~/.android/cache/*",
        "~/.android/build-cache/*",
    ]
    for p in targets:
        rm_glob(os.path.expanduser(p), apply)
    return 0


def mediaanalysisd_cache(apply: bool) -> int:
    print("== mediaanalysisd cache cleanup ==")
    target = "~/Library/Containers/com.apple.mediaanalysisd/Data/Library/Caches/*"
    rm_glob(os.path.expanduser(target), apply)
    return 0


def list_snapshots() -> int:
    print("== Time Machine local snapshots ==")
    return subprocess.call(["/usr/bin/tmutil", "listlocalsnapshots", "/"])


def delete_snapshot(snapshot_id: str, apply: bool) -> int:
    cmd = ["/usr/bin/tmutil", "deletelocalsnapshots", snapshot_id]
    return run_cmd(cmd, apply)


def main() -> int:
    parser = argparse.ArgumentParser(description="macOS storage cleanup helper")
    parser.add_argument("--diagnose", action="store_true", help="show large folders (read-only)")
    parser.add_argument("--safe-clean", action="store_true", help="clean safe caches/logs")
    parser.add_argument("--dev-clean", action="store_true", help="clean dev caches")
    parser.add_argument("--mediaanalysisd-cache", action="store_true", help="clean mediaanalysisd cache")
    parser.add_argument("--list-snapshots", action="store_true", help="list Time Machine local snapshots")
    parser.add_argument("--delete-snapshot", metavar="ID", help="delete a Time Machine local snapshot")
    parser.add_argument("--all", action="store_true", help="run diagnose + safe + dev + mediaanalysisd")
    parser.add_argument("--apply", action="store_true", help="execute actions (default is dry-run)")

    args = parser.parse_args()
    apply = args.apply

    if args.all:
        diagnose()
        safe_clean(apply)
        dev_clean(apply)
        mediaanalysisd_cache(apply)
        return 0

    if args.diagnose:
        diagnose()
    if args.safe_clean:
        safe_clean(apply)
    if args.dev_clean:
        dev_clean(apply)
    if args.mediaanalysisd_cache:
        mediaanalysisd_cache(apply)
    if args.list_snapshots:
        list_snapshots()
    if args.delete_snapshot:
        delete_snapshot(args.delete_snapshot, apply)

    if not any(
        [
            args.diagnose,
            args.safe_clean,
            args.dev_clean,
            args.mediaanalysisd_cache,
            args.list_snapshots,
            args.delete_snapshot,
            args.all,
        ]
    ):
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
