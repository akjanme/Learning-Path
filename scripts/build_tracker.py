"""Generate TRACKER.md, QUESTION-BANK.md and tracker.csv from the sprint files."""
import csv
import re
import sys
from collections import OrderedDict
from pathlib import Path

root = Path(sys.argv[1])
sprint_files = sorted((root / "sprints").glob("sprint-*.md"))

day_re = re.compile(r"^### Day (\d+) · (.+?) · (.+)$")
sprint_title_re = re.compile(r"^# Sprint (\d+) — (.+?) \(Days")
q_re = re.compile(r"^\d+\. \*\*(.+?)\*\*(?: — (.+))?$")

days = []
sprints = []
for f in sprint_files:
    lines = f.read_text(encoding="utf-8").splitlines()
    m = sprint_title_re.match(lines[0])
    sprint_no, sprint_name = int(m.group(1)), m.group(2)
    sprints.append((sprint_no, sprint_name, f.name))
    current = None
    in_q = False
    for line in lines:
        dm = day_re.match(line)
        if dm:
            current = {
                "day": int(dm.group(1)),
                "track": dm.group(2),
                "topic": dm.group(3),
                "sprint": sprint_no,
                "sprint_name": sprint_name,
                "file": f.name,
                "questions": [],
                "time": "",
            }
            days.append(current)
            in_q = False
            continue
        if current is None:
            continue
        if line.startswith("**Time:**"):
            current["time"] = line.replace("**Time:**", "").strip()
        if line.strip() == "**Interview questions**":
            in_q = True
            continue
        if in_q:
            qm = q_re.match(line.strip())
            if qm:
                current["questions"].append((qm.group(1), qm.group(2) or ""))
            elif line.strip().startswith("**") or line.strip() == "---":
                in_q = False

# sanity checks
nums = [d["day"] for d in days]
assert nums == list(range(1, len(nums) + 1)), f"day numbering broken: {nums}"


def track_group(track):
    if track.startswith("Mock interview"):
        return "Mock interview"
    return track


# ---------- TRACKER.md ----------
out = ["# Progress tracker", ""]
out.append(
    "Tick a day when its **Done when** line is true, not when you've watched the videos. "
    "Days are numbered, not dated: do them at your own pace and in order within a sprint."
)
out.append("")
total = len(days)
out.append(f"**Total:** {total} days in {len(sprints)} sprints · ~2–4 h per day")
out.append("")
out.append("| Sprint | Days | Scenario |")
out.append("| --- | --- | --- |")
for no, name, fname in sprints:
    sd = [d["day"] for d in days if d["sprint"] == no]
    out.append(f"| {no} | {sd[0]}–{sd[-1]} | [{name}](sprints/{fname}) |")
out.append("")
out.append("Track legend: Cloud · AI · DevOps · MLOps · .NET + Design · Build + Defend · Capstone · Interview prep · Mock interview")
out.append("")
for no, name, fname in sprints:
    out.append(f"## Sprint {no} — {name}")
    out.append("")
    for d in [d for d in days if d["sprint"] == no]:
        out.append(
            f"- [ ] **Day {d['day']}** · {d['track']} · [{d['topic']}](sprints/{fname}#day-{d['day']})"
        )
    out.append("")
out.append("---")
out.append("")
out.append("Sprint retro (copy after each sprint):")
out.append("")
out.append("```")
out.append("Sprint N retro")
out.append("- Built: ")
out.append("- Hardest thing: ")
out.append("- Interview answers still weak: ")
out.append("- Carry over: ")
out.append("```")
(root / "TRACKER.md").write_text("\n".join(out) + "\n", encoding="utf-8")

# ---------- QUESTION-BANK.md ----------
groups = OrderedDict()
order = ["Cloud", "AI", "DevOps", "MLOps", ".NET + Design", "Build + Defend", "Capstone", "Interview prep", "Mock interview"]
for g in order:
    groups[g] = []
for d in days:
    groups.setdefault(track_group(d["track"]), []).append(d)

titles = {
    "Build + Defend": "Sprint scenarios (Build + Defend days)",
    "Interview prep": "Interview-sprint rehearsal questions",
    "Mock interview": "Mock interview questions",
}
qb = ["# Interview question bank", ""]
count = sum(len(d["questions"]) for d in days)
qb.append(
    f"All {count} interview questions from the plan, grouped by track, each with its answer hint and a link to the day that teaches it. "
    "Practise out loud: cover the hint, answer in 3–5 minutes, then compare."
)
qb.append("")
for g, ds in groups.items():
    ds = [d for d in ds if d["questions"]]
    if not ds:
        continue
    qb.append(f"## {titles.get(g, g)}")
    qb.append("")
    for d in ds:
        qb.append(f"**Day {d['day']} — [{d['topic']}](sprints/{d['file']}#day-{d['day']})**")
        qb.append("")
        for q, hint in d["questions"]:
            qb.append(f"- [ ] {q}")
            if hint:
                qb.append(f"  - *Hint:* {hint}")
        qb.append("")
(root / "QUESTION-BANK.md").write_text("\n".join(qb) + "\n", encoding="utf-8")

# ---------- tracker.csv ----------
with open(root / "tracker.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["Day", "Sprint", "Sprint name", "Track", "Topic", "Est. time", "Status", "Date done", "Confidence (1-5)", "Notes", "Link"])
    for d in days:
        w.writerow([
            d["day"], d["sprint"], d["sprint_name"], track_group(d["track"]), d["topic"], d["time"],
            "Not started", "", "", "", f"sprints/{d['file']}#day-{d['day']}",
        ])

print(f"days={len(days)} questions={count} sprints={len(sprints)}")
for g, ds in groups.items():
    print(g, len(ds))
