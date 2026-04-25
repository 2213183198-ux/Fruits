from __future__ import annotations

import sys

from legacy_launcher import forward_to_cli


if __name__ == "__main__":
    forward_to_cli("train", sys.argv[1:])
