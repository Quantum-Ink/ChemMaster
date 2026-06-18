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

    # 数据文件：前端、插件、语言包
    # 注意：backend 作为 Python 包处理，不作为数据文件
    datas = [
        ("frontend", "frontend"),
        ("plugins", "plugins"),
        ("desktop/locales", "desktop/locales"),
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

    # 添加项目根目录到 Python 搜索路径（分析阶段发现 backend 包）
    args.extend(["--paths", str(PROJECT_ROOT)])

    # 添加数据文件
    for src, dst in datas:
        src_path = PROJECT_ROOT / src
        if src_path.exists():
            args.extend(["--add-data", f"{src_path}{os.pathsep}{dst}"])

    # 收集 backend 子模块（确保 PyInstaller 能分析到所有后端模块）
    args.extend(["--collect-submodules", "backend"])

    # 隐式导入：PyInstaller 无法自动发现的依赖
    hidden_imports = [
        # uvicorn 子模块
        "uvicorn", "uvicorn.logging", "uvicorn.loops", "uvicorn.loops.auto",
        "uvicorn.protocols", "uvicorn.protocols.http", "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets", "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan", "uvicorn.lifespan.on",
        # 核心依赖
        "fastapi", "pydantic", "aiosqlite",
        "webview", "pystray",
        "rdkit", "numpy", "requests",
        # 后端模块（确保打包完整）
        "backend", "backend.app", "backend.app.main",
        "backend.app.api", "backend.app.api.editor", "backend.app.api.export",
        "backend.app.api.structure", "backend.app.api.data", "backend.app.api.ion",
        "backend.app.core", "backend.app.core.chemistry", "backend.app.core.reaction_engine",
        "backend.app.core.ion_engine", "backend.app.core.rdkit_engine",
        "backend.app.core.molecule_renderer", "backend.app.core.pubchem_api",
        "backend.app.core.equation_enhancer",
        "backend.app.data", "backend.app.data.database", "backend.app.data.models",
        "backend.app.data.cache", "backend.app.data.offline_store", "backend.app.data.seed_data",
        "backend.app.plugins", "backend.app.plugins.base",
        "backend.app.plugins.latex_plugin", "backend.app.plugins.word_plugin",
        "backend.app.plugins.structure_plugin", "backend.app.plugins.reaction_predict_plugin",
        "backend.app.services", "backend.app.services.plugin_manager",
        # 桌面模块
        "desktop", "desktop.app", "desktop.tray", "desktop.i18n",
    ]
    for imp in hidden_imports:
        args.extend(["--hidden-import", imp])

    # 入口脚本
    args.append(str(PROJECT_ROOT / "run.py"))

    print(f"\nRunning PyInstaller build...")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Output: {DIST_DIR}\n")

    result = subprocess.run(args, cwd=str(PROJECT_ROOT))

    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("Build SUCCESS!")
        exe_name = "ChemMaster.exe" if sys.platform == "win32" else "ChemMaster"
        exe_path = DIST_DIR / exe_name
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Output: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
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
