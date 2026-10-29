#!/usr/bin/env python3
"""Erzeugt synthetische sshd-Logs mit normalem Betrieb und Brute-Force-Angriffen.

Aufruf:  python scripts/generate_logs.py --out logs/auth.log --days 1 --seed 42
"""
import argparse
import random
from datetime import datetime, timedelta

USERS = ["alice", "bob", "carol", "deploy", "backup"]
ATTACK_USERS = ["root", "admin", "test", "ubuntu", "oracle", "alice"]
HOST = "srv-lab-01"


def line(ts, msg, pid):
    return f"{ts:%Y-%m-%d %H:%M:%S} {HOST} sshd[{pid}]: {msg}"


def generate(days, seed):
    rnd = random.Random(seed)
    end = datetime.now().replace(microsecond=0)
    start = end - timedelta(days=days)
    events = []

    # Normalbetrieb: meist erfolgreiche Anmeldungen, selten ein Tippfehler
    t = start
    while t < end:
        t += timedelta(minutes=rnd.randint(3, 25))
        user = rnd.choice(USERS)
        ip = f"10.0.{rnd.randint(0, 3)}.{rnd.randint(2, 50)}"
        port = rnd.randint(40000, 65000)
        if rnd.random() < 0.08:
            events.append((t, f"Failed password for {user} from {ip} port {port} ssh2"))
        events.append((t + timedelta(seconds=3), f"Accepted password for {user} from {ip} port {port} ssh2"))

    # Brute-Force-Angriffe: viele Fehlversuche in wenigen Minuten
    for _ in range(max(2, days * 2)):
        attacker = f"203.0.113.{rnd.randint(1, 254)}"
        t0 = start + timedelta(seconds=rnd.randint(0, int((end - start).total_seconds()) - 600))
        for i in range(rnd.randint(12, 40)):
            user = rnd.choice(ATTACK_USERS)
            inv = "invalid user " if user not in USERS else ""
            events.append((t0 + timedelta(seconds=i * rnd.randint(2, 6)),
                           f"Failed password for {inv}{user} from {attacker} port {rnd.randint(30000, 60000)} ssh2"))
        # In einem Teil der Faelle gelingt der Angriff am Ende
        if rnd.random() < 0.5:
            events.append((t0 + timedelta(minutes=4), f"Accepted password for alice from {attacker} port {rnd.randint(30000, 60000)} ssh2"))

    events.sort(key=lambda e: e[0])
    return [line(ts, msg, rnd.randint(1000, 9999)) for ts, msg in events]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="logs/auth.log")
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    lines = generate(a.days, a.seed)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"{len(lines)} Zeilen nach {a.out} geschrieben")
