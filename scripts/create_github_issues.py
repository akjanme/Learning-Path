"""Create one GitHub issue per study day from tracker.csv.

Usage:
  python scripts/create_github_issues.py --repo owner/name          # preview only
  python scripts/create_github_issues.py --repo owner/name --apply  # create labels + issues

Requires the GitHub CLI (`gh`) logged in with access to the repo.
"""
import argparse
import csv
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--repo", required=True, help="owner/name")
parser.add_argument("--apply", action="store_true", help="actually create labels and issues")
parser.add_argument("--csv", default=str(Path(__file__).resolve().parent.parent / "tracker.csv"))
args = parser.parse_args()

rows = list(csv.DictReader(open(args.csv, encoding="utf-8")))
labels = sorted({f"sprint-{int(r['Sprint']):02d}" for r in rows} | {f"track:{r['Track']}" for r in rows})


def run(cmd):
    if args.apply:
        subprocess.run(cmd, check=False)
    else:
        print("DRY RUN:", " ".join(cmd))


for label in labels:
    run(["gh", "label", "create", label, "--repo", args.repo, "--force"])

for r in rows:
    title = f"Day {r['Day']} · {r['Track']} · {r['Topic']}"
    body = (
        f"**Sprint {r['Sprint']}: {r['Sprint name']}**\n\n"
        f"Plan: https://github.com/{args.repo}/blob/main/{r['Link']}\n\n"
        f"Estimated time: {r['Est. time']}\n\n"
        "Close this issue when the day's **Done when** line is true. "
        "Add a comment with what you built and anything still unclear."
    )
    run([
        "gh", "issue", "create", "--repo", args.repo, "--title", title, "--body", body,
        "--label", f"sprint-{int(r['Sprint']):02d}", "--label", f"track:{r['Track']}",
    ])

print(f"{'Created' if args.apply else 'Previewed'} {len(rows)} issues and {len(labels)} labels.")
