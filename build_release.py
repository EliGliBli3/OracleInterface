import shutil
import subprocess
from pathlib import Path
from subprocess import run

import sys
import zipfile

from update_handler import APP_VERSION
from logger import *

PROJECT_DIR = Path(__file__).parent.resolve()

VENV_DIR = PROJECT_DIR / ".venv"
PYTHON_EXE = VENV_DIR / "Scripts" / "python.exe"

DIST_DIR = PROJECT_DIR / "dist"
BUILD_PACKAGE = PROJECT_DIR / "build_package"

APP_DIST = DIST_DIR / "main"

ZIP_NAME = f"OracleInterface-{APP_VERSION}.zip"
ZIP_PATH = DIST_DIR / ZIP_NAME
SETUP_ZIP_NAME = f"OracleInterface-{APP_VERSION}-setup.zip"
SETUP_ZIP_PATH = DIST_DIR / SETUP_ZIP_NAME


def setup_environment():
    # Create VENV if it doesn't exist (in the case of a new local dev environment)
    if not VENV_DIR.exists():
        subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            cwd=PROJECT_DIR,
            check=True
        )

    # Install package requirements
    run([
        str(PYTHON_EXE),
        "-m",
        "pip",
        "install",
        "-r",
        "requirements.txt"
    ])

def build():
    # Build application ZIP
    run([
        str(PYTHON_EXE),
        "-m",
        "PyInstaller",
        "--onedir",
        "--collect-all",
        "playwright",
        "main.py",
        "-y"
    ])

    # Build updater ZIP
    run([
        str(PYTHON_EXE),
        "-m",
        "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name",
        "Updater",
        "update_handler.py",
        "-y"
    ])

def prepare_dist():
    APP_DIST.mkdir(parents=True, exist_ok=True)

    # Copy build package (readme + shortcut generator script)
    robo = subprocess.run([
        "robocopy",
        str(BUILD_PACKAGE),
        str(DIST_DIR),
        "/e"
    ], cwd=PROJECT_DIR)

    # robocopy codes are failures above code #7... don't ask me why
    if robo.returncode >= 8:
        err_break(f"Robocopy failed with code {robo.returncode}")

    # Create logs directory for first-time setups where 'logs' doesn't already exist
    (APP_DIST / "logs").mkdir(
        parents=True,
        exist_ok=True
    )

    # Copy updater into the main folder
    updater_source = DIST_DIR / "Updater.exe"
    updater_destination = APP_DIST / "Updater.exe"

    if not updater_source.exists():
        raise FileNotFoundError(
            f"Updater executable not found: {updater_source}"
        )

    shutil.copy2(
        updater_source,
        updater_destination
    )

    # Generate installed version file
    (APP_DIST / "version.txt").write_text(
        APP_VERSION,
        encoding="utf-8"
    )

def _add_files(archive, root, arc_prefix=None, skip=None):
    skip = skip or set()

    for file in root.rglob("*"):
        if not file.is_file():
            continue

        relative = file.relative_to(root)
        parts_lower = tuple(part.lower() for part in relative.parts)

        if parts_lower in skip or parts_lower[0] in skip:
            continue

        archive_name = (
            (Path(arc_prefix) / relative).as_posix()
            if arc_prefix
            else relative.as_posix()
        )
        archive.write(file, archive_name)


def package_release():
    # contents of dist/main except Updater.exe and logs/
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(
            ZIP_PATH,
            "w",
            compression=zipfile.ZIP_DEFLATED
    ) as archive:
        _add_files(
            archive,
            APP_DIST,
            skip={"updater.exe", "logs"}
        )

    # first-time setup -> readme, genShortcuts, main/, and Updater.exe
    if SETUP_ZIP_PATH.exists():
        SETUP_ZIP_PATH.unlink()

    with zipfile.ZipFile(
            SETUP_ZIP_PATH,
            "w",
            compression=zipfile.ZIP_DEFLATED
    ) as archive:
        _add_files(archive, APP_DIST, arc_prefix="main")

        for item in BUILD_PACKAGE.iterdir():
            dest = DIST_DIR / item.name
            if dest.is_file():
                archive.write(dest, dest.name)
            elif dest.is_dir():
                _add_files(archive, dest, arc_prefix=dest.name)

if __name__ == "__main__":
    try:
        log(f"\nBuilding Oracle Interface {APP_VERSION}\n{"="*50}", LogLevel.PENDING)

        setup_environment()
        build()
        prepare_dist()
        package_release()

        log(f"\n{"="*50}")
        log("BUILD COMPLETED SUCCESSFULLY", LogLevel.SUCCESS)
        log(f"Version: {APP_VERSION}")
        log(f"Update payload: {ZIP_PATH}")
        log(f"First-time setup: {SETUP_ZIP_PATH}")
        log("=" * 50)

    except Exception as error:
        err_break(f"\nBUILD FAILED\n{error}")