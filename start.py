from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print(f"\n> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    if shutil.which("docker") is None:
        print("未检测到 docker，请先安装并启动 Docker Desktop。")
        return 1

    run(["docker", "compose", "up", "--build", "-d"])

    print("\nFruits 项目已启动：")
    print("Web:  http://127.0.0.1:8001/")
    print("Docs: http://127.0.0.1:8001/docs")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"\n启动失败，命令退出码：{exc.returncode}")
        raise SystemExit(exc.returncode)
