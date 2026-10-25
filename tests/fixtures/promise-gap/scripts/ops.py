#!/usr/bin/env python3
"""Fixture script: implements check_lead only; imports smtplib with no guard.

The comma-separated import mirrors real-world scripts and is a regression
guard for the capability scanner.
"""

import smtplib, sys  # noqa: E401,F401  (intentional: EXT.1 bait, never used)


def cmd_check_lead(email: str) -> None:
    print(f"OK {email}")


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check_lead":
        cmd_check_lead(sys.argv[2] if len(sys.argv) > 2 else "")
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
