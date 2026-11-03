import argparse
import hashlib
import os
import shutil
import subprocess
import tempfile
import time
import zipfile
from datetime import datetime
from pathlib import Path

import requests
import sys

APP_VERSION = "1.0.1"
FROZEN = getattr(sys, "frozen", False)

GITHUB_OWNER = "EliGliBli3"
GITHUB_REPO = "OracleInterface"

API_URL = (
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
)

APP_DIR = Path(sys.executable).parent
VERSION_RECORD = APP_DIR / "version.txt"


def get_installed_version():
    if not VERSION_RECORD.exists():
        return "0.0.0"

    return VERSION_RECORD.read_text(encoding="utf-8").strip()


def parse_version(version):
    return tuple(
        int(part)
        for part in version.lstrip("vV").split(".")
    )


def get_latest_release():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "OracleInterface-Updater"
    }

    response = requests.get(API_URL, headers=headers, timeout=15)
    response.raise_for_status()

    return response.json()


def download_update(url, destination):
    digest = hashlib.sha256()

    with requests.get(
        url,
        headers={"User-Agent": "OracleInterface-Updater"},
        timeout=60,
        stream=True
    ) as response:
        response.raise_for_status()
        with open(destination, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue

                file.write(chunk)
                digest.update(chunk)

    return digest.hexdigest()


def _installer_log(message):
    log_dir = APP_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_dir / "updater.log", "a", encoding="utf-8") as file:
        file.write(f"{stamp} {message}\n")


def wait_for_pid(pid, timeout_seconds=120):
    if pid <= 0:
        return

    if sys.platform == "win32":
        import ctypes

        synchronize = 0x00100000
        wait_timeout = 0x00000102
        handle = ctypes.windll.kernel32.OpenProcess(synchronize, False, pid)
        if not handle:
            return

        try:
            result = ctypes.windll.kernel32.WaitForSingleObject(
                handle,
                int(timeout_seconds * 1000)
            )
            if result == wait_timeout:
                raise TimeoutError(
                    f"Process {pid} did not exit within {timeout_seconds}s"
                )
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
        return

    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            os.kill(pid, 0)
        except OSError:
            return

        if time.monotonic() > deadline:
            raise TimeoutError(
                f"Process {pid} did not exit within {timeout_seconds}s"
            )

        time.sleep(0.2)


def _safe_extract_member(archive, info, destination):
    name = info.filename.replace("\\", "/").lstrip("/")
    if not name or name.endswith("/"):
        return

    lower = name.lower()
    if lower == "updater.exe" or lower.startswith("logs/"):
        return

    target = (destination / name).resolve()
    if not target.is_relative_to(destination.resolve()):
        raise RuntimeError(f"Refusing path traversal: {info.filename}")

    target.parent.mkdir(parents=True, exist_ok=True)
    with archive.open(info) as source, open(target, "wb") as output:
        shutil.copyfileobj(source, output)


def install_update(zip_path, pid, version):
    zip_path = Path(zip_path)
    _installer_log(f"Installing {version} from {zip_path}")

    wait_for_pid(pid)

    if not zip_path.is_file():
        raise FileNotFoundError(f"Update zip not found: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as archive:
        for info in archive.infolist():
            _safe_extract_member(archive, info, APP_DIR)

    if version:
        VERSION_RECORD.write_text(version, encoding="utf-8")

    main_exe = APP_DIR / "main.exe"
    if not main_exe.exists():
        raise FileNotFoundError(f"Updated executable not found: {main_exe}")

    subprocess.Popen(
        [str(main_exe)],
        cwd=str(APP_DIR)
    )
    _installer_log(f"Installed {version} and relaunched {main_exe}")


def check_for_updates():
    if not FROZEN:
        return False

    try:
        installed_version = get_installed_version()
        release = get_latest_release()
        latest_version = release["tag_name"].lstrip("vV")

        if parse_version(latest_version) <= parse_version(installed_version):
            return False

        expected_name = f"OracleInterface-{latest_version}.zip"

        asset = next(
            (
                item
                for item in release["assets"]
                if item["name"] == expected_name
            ),
            None
        )

        if not asset:
            return False

        expected_digest = asset.get("digest")

        if not expected_digest or not expected_digest.startswith("sha256:"):
            return False

        updater_path = APP_DIR / "Updater.exe"
        if not updater_path.exists():
            return False

        update_dir = Path(tempfile.gettempdir()) / "OracleInterfaceUpdates"
        update_dir.mkdir(parents=True, exist_ok=True)

        zip_path = update_dir / expected_name

        actual_digest = download_update(
            asset["browser_download_url"],
            zip_path
        )

        if actual_digest.lower() != expected_digest[7:].lower():
            zip_path.unlink(missing_ok=True)
            return False

        subprocess.Popen([
            str(updater_path),
            "--install",
            str(zip_path),
            "--pid",
            str(os.getpid()),
            "--version",
            latest_version
        ])

        return True

    except Exception as error:
        print(f"Update check failed: {error}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Oracle Interface updater")
    parser.add_argument("--install", required=True, type=Path)
    parser.add_argument("--pid", required=True, type=int)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()

    try:
        install_update(args.install, args.pid, args.version)
    except Exception as error:
        _installer_log(f"Install failed: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
