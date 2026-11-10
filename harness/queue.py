#!/usr/bin/env python3
"""Question queue: how the run handles the questions each result raises.

  python harness/queue.py add '{"question": "...", "engine": "C", "value": 4, "p_informative": 0.5, "cost_hours": 6, "cost_usd": 10, ...}'
  python harness/queue.py list [--all]
  python harness/queue.py show Q003
  python harness/queue.py update Q003 status=answered "result=no effect at 10 uM"
  python harness/queue.py seal Q011 [--git]     # freeze the card's prediction before its test
Exploration-lane ideas enter as cards with engine "F" and must be sealed before testing.
Priority = value * p_informative / (1 + cost_hours/8 + cost_usd/25 + 2*manav_hours/8). The planner
may set priority_override with a reason.
"""
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
Q = ROOT / "questions" / "queue.jsonl"


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load():
    return [json.loads(l) for l in Q.read_text().splitlines() if l.strip()] if Q.exists() else []


def save(cards):
    Q.parent.mkdir(exist_ok=True)
    tmp = Q.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(c, sort_keys=True) + "\n" for c in cards))
    tmp.replace(Q)


def num(c, k, d=0.0):
    try:
        return float(c.get(k, d) or d)
    except (TypeError, ValueError):
        return d


def priority(c):
    if c.get("priority_override") is not None:
        return float(c["priority_override"])
    return num(c, "value", 1) * num(c, "p_informative", 0.5) / (
        1 + num(c, "cost_hours") / 8 + num(c, "cost_usd") / 25 + 2 * num(c, "manav_hours") / 8)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    cards = load()
    if cmd == "add":
        c = json.loads(args[0])
        if "question" not in c:
            sys.exit("card needs a question")
        c.setdefault("id", f"Q{len(cards) + 1:03d}")
        if any(x["id"] == c["id"] for x in cards):
            sys.exit(f"{c['id']} exists")
        c.setdefault("status", "open")
        c["created"] = c["updated"] = now()
        cards.append(c)
        save(cards)
        print(c["id"])
    elif cmd == "list":
        show = cards if "--all" in args else [c for c in cards if c.get("status") in ("open", "running")]
        for c in sorted(show, key=priority, reverse=True):
            print(f"{c['id']}  {priority(c):6.3f}  {c.get('status',''):<9} {c.get('engine',''):<3} {c['question'][:90]}")
    elif cmd == "show":
        print(json.dumps(next((c for c in cards if c["id"] == args[0]), {}), indent=2))
    elif cmd == "update":
        c = next((c for c in cards if c["id"] == args[0]), None)
        if not c:
            sys.exit("no such card")
        for kv in args[1:]:
            k, v = kv.split("=", 1)
            if k == "prediction" and c.get("seal_name"):
                sys.exit("prediction is sealed; add a new card instead")
            c[k] = v
        c["updated"] = now()
        save(cards)
    elif cmd == "seal":
        import subprocess
        c = next((c for c in cards if c["id"] == args[0]), None)
        if not c:
            sys.exit("no such card")
        if c.get("seal_name"):
            sys.exit(f"already sealed as {c['seal_name']}")
        if not c.get("prediction") or not c.get("kill_criterion"):
            sys.exit("a card needs a prediction and a kill_criterion before sealing")
        d = ROOT / "questions" / "sealed_cards"
        d.mkdir(exist_ok=True)
        f = d / f"{c['id']}.json"
        f.write_text(json.dumps({k: c[k] for k in ("id", "question", "prediction", "kill_criterion", "cheapest_test", "evidence_tier") if k in c}, indent=2, sort_keys=True))
        name = f"card_{c['id']}"
        cmd2 = [sys.executable, str(ROOT / "harness/seal.py"), str(f), "--name", name] + (["--git"] if "--git" in args else [])
        r = subprocess.run(cmd2, capture_output=True, text=True)
        print(r.stdout + r.stderr)
        if r.returncode != 0:
            sys.exit(1)
        c["seal_name"] = name
        c["updated"] = now()
        save(cards)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
