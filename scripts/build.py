"""
ChemMaster 打包脚本
使用 PyInstaller 生成独立可执行文件

用法：
    python scripts/build.py              # 打包当前平台
    python scripts/build.py --clean      # 清理构建目录
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_FILE = PROJECT_ROOT / "chemmaster.spec"


def clean():
    """清理构建目录"""
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
            print(f"Cleaned: {d}")
    if SPEC_FILE.exists():
        SPEC_FILE.unlink()
        print(f"Cleaned: {SPEC_FILE}")


def build():
    """执行 PyInstaller 打包"""
    print("=" * 50)
    print("ChemMaster Desktop Build")
    print("=" * 50)

    # 收集数据文件
    datas = [
        ("frontend", "frontend"),
        ("plugins", "plugins"),
        ("desktop/locales", "desktop/locales"),
        ("backend", "backend"),
    ]

    # 构建 PyInstaller 参数
    args = [
        sys.executable, "-m", "PyInstaller",
        "--name", "ChemMaster",
        "--onefile",                    # 单文件
        "--windowed",                   # 无控制台窗口（Windows/macOS）
        "--noconfirm",                  # 不确认覆盖
        "--clean",                      # 清理缓存
    ]

    # 添加数据文件
    for src, dst in datas:
        src_path = PROJECT_ROOT / src
        if src_path.exists():
            args.extend(["--add-data", f"{src_path};{dst}"])

    # 添加隐式导入
    hidden_imports = [
        "uvicorn", "uvicorn.logging", "uvicorn.loops", "uvicorn.loops.auto",
        "uvicorn.protocols", "uvicorn.protocols.http", "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets", "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan", "uvicorn.lifespan.on",
        "fastapi", "pydantic", "aiosqlite",
        "webview", "pystray",
        "rdkit", "numpy", "requests",
    ]
    for imp in hidden_imports:
        args.extend(["--hidden-import", imp])

    # 入口脚本
    args.append(str(PROJECT_ROOT / "run.py"))

    print(f"\nRunning: {' '.join(args[:5])}...")
    print(f"Output: {DIST_DIR}\n")

    result = subprocess.run(args, cwd=str(PROJECT_ROOT))

    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("Build SUCCESS!")
        exe_name = "ChemMaster.exe" if sys.platform == "win32" else "ChemMaster"
        print(f"Output: {DIST_DIR / exe_name}")
        print("=" * 50)
    else:
        print("\nBuild FAILED!")
        sys.exit(1)


def main():
    if "--clean" in sys.argv:
        clean()
    else:
        build()


if __name__ == "__main__":
    main()
