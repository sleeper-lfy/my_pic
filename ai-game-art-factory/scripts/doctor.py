#!/usr/bin/env python3
"""Read-only, bounded environment probes. No downloads or software changes."""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


def run(command: list[str], timeout: int = 15) -> dict:
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                errors="replace", timeout=timeout, check=False)
        return {"ok": result.returncode == 0, "exit_code": result.returncode,
                "output": (result.stdout + result.stderr).strip()[:4000]}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"ok": False, "error": type(error).__name__}


def executable(names: list[str]) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    if platform.system() != "Windows":
        return None
    # Bounded known installation folders; never recurse through user disks.
    roots = [Path(os.environ.get("ProgramFiles", "C:/Program Files")),
             Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData/Local")))]
    patterns = {"blender": ["Blender Foundation/Blender */blender.exe"],
                "godot": ["Godot/godot.exe", "Godot/Godot*.exe"],
                "ffmpeg": ["ffmpeg/bin/ffmpeg.exe"],
                "magick": ["ImageMagick*/magick.exe"],
                "inkscape": ["Inkscape/bin/inkscape.exe"]}
    for root in roots:
        for pattern in patterns.get(names[0], []):
            for candidate in sorted(root.glob(pattern), reverse=True)[:10]:
                if candidate.is_file():
                    return str(candidate)
    # App Paths is an official Windows application registration location.
    try:
        import winreg
        for hive in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
            for name in names:
                key = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\" + name + ".exe"
                try:
                    with winreg.OpenKey(hive, key) as opened:
                        value, _ = winreg.QueryValueEx(opened, None)
                        candidate = Path(value.strip('"'))
                        if candidate.is_file():
                            return str(candidate)
                except OSError:
                    pass
    except ImportError:
        pass
    return None


def probe_tool(names: list[str], version_args: list[str]) -> dict:
    path = executable(names)
    if path is None:
        return {"available": False, "status": "not_discovered"}
    result = run([path, *version_args])
    return {"available": result["ok"], "path": path,
            "version": result.get("output", "").splitlines()[:3],
            "probe": result}


def json_endpoint(base: str, endpoint: str) -> dict:
    # Local ComfyUI should not pass through an HTTP proxy.
    class LocalOnlyRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            if urllib.parse.urlsplit(newurl).hostname not in {"localhost", "127.0.0.1", "::1"}:
                raise ValueError("non_loopback_redirect_rejected")
            return super().redirect_request(req, fp, code, msg, headers, newurl)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), LocalOnlyRedirect())
    request = urllib.request.Request(base.rstrip("/") + endpoint,
                                     headers={"Accept": "application/json"})
    try:
        with opener.open(request, timeout=4) as response:
            data = response.read(8 * 1024 * 1024 + 1)
            if len(data) > 8 * 1024 * 1024:
                return {"ok": False, "error": "response_exceeds_8_MiB_limit"}
            parsed = json.loads(data)
            if not isinstance(parsed, dict):
                return {"ok": False, "error": "unexpected_json_type"}
            return {"ok": True, "data": parsed}
    except (OSError, urllib.error.URLError, ValueError) as error:
        # Do not echo response bodies or potentially credential-bearing URLs.
        return {"ok": False, "error": type(error).__name__,
                "reason_type": type(getattr(error, "reason", error)).__name__}


def probe_comfy(url: str) -> dict:
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme not in {"http", "https"} or
            parsed.hostname not in {"localhost", "127.0.0.1", "::1"} or
            parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise ValueError("--comfy-url must be a credential-free loopback HTTP(S) URL")
    stats = json_endpoint(url, "/system_stats")
    nodes = json_endpoint(url, "/object_info")
    report = {"url": url, "system_stats_ok": stats["ok"],
              "object_info_ok": nodes["ok"],
              "available": stats["ok"] and nodes["ok"]}
    if stats["ok"]:
        system = stats["data"].get("system", {})
        report["versions"] = {k: system.get(k) for k in
                              ["comfyui_version", "python_version", "pytorch_version"]}
        report["devices"] = [{k: d.get(k) for k in ["type", "vram_total", "vram_free"]}
                             for d in stats["data"].get("devices", [])]
    else:
        report["system_stats_error"] = stats.get("error")
        report["system_stats_reason"] = stats.get("reason_type")
    if nodes["ok"]:
        classes = nodes["data"]
        expected = ["CheckpointLoaderSimple", "ControlNetLoader", "ControlNetApplyAdvanced",
                    "KSampler", "LoadImage", "SaveImage", "VAEEncode", "VAEDecode"]
        report["node_class_count"] = len(classes)
        report["core_nodes_present"] = {name: name in classes for name in expected}
        report["model_inventory"] = "not_collected; model license and suitability require separate review"
    else:
        report["object_info_error"] = nodes.get("error")
        report["object_info_reason"] = nodes.get("reason_type")
    candidates = [Path("/workspace/ComfyUI"), Path("/opt/ComfyUI"),
                  Path.home() / "ComfyUI", Path.home() / "Documents/ComfyUI",
                  Path.home() / "ComfyUI_windows_portable/ComfyUI"]
    report["known_installations"] = [str(p) for p in candidates if (p / "main.py").is_file()]
    report["installation_search_scope"] = "PATH-independent bounded common folders only; absence is not proof of non-installation"
    report["launch_guidance"] = "Use the existing installation's documented launcher or its own Python environment; no generic launch command has been verified."
    return report


def collect(url: str) -> dict:
    tools = {
        "blender": probe_tool(["blender"], ["--version"]),
        "godot": probe_tool(["godot", "godot4"], ["--headless", "--version"]),
        "ffmpeg": probe_tool(["ffmpeg"], ["-version"]),
        "imagemagick": probe_tool(["magick", "convert"], ["-version"]),
        "inkscape": probe_tool(["inkscape"], ["--version"]),
        "aseprite": probe_tool(["aseprite"], ["--version"]),
        "krita": probe_tool(["krita"], ["--version"]),
    }
    if tools["blender"]["available"]:
        expression = "import bpy,sys; print('ART_FACTORY_BLENDER_PROBE='+bpy.app.version_string+';python='+sys.version.split()[0])"
        runtime = run([tools["blender"]["path"], "--background", "--factory-startup",
                       "--python-expr", expression], timeout=40)
        tools["blender"]["python_execution"] = {
            "ok": runtime["ok"] and "ART_FACTORY_BLENDER_PROBE=" in runtime.get("output", ""),
            "command_pattern": "blender --background --factory-startup --python path/to/script.py -- [script arguments]",
            "probe": runtime,
        }
    modules = {}
    for module, distribution in [("PIL", "Pillow"), ("numpy", "numpy"), ("yaml", "PyYAML"),
                                 ("cv2", "opencv-python"), ("torch", "torch")]:
        present = importlib.util.find_spec(module) is not None
        try:
            version = importlib.metadata.version(distribution) if present else None
        except importlib.metadata.PackageNotFoundError:
            version = "unknown"
        modules[module] = {"available": present, "version": version}
    gpu_path = executable(["nvidia-smi"])
    gpu = run([gpu_path, "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
              timeout=10) if gpu_path else {"ok": False, "status": "nvidia_smi_not_discovered"}
    comfy = probe_comfy(url)
    return {
        "schema_version": 1,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope": "This execution host only; does not inspect another machine or the user's Windows PC.",
        "host": {"platform": platform.platform(), "system": platform.system(),
                 "machine": platform.machine(), "logical_cpu_count": os.cpu_count()},
        "python": {"executable": sys.executable, "version": platform.python_version(), "modules": modules},
        "tools": tools,
        "gpu": gpu,
        "comfyui": comfy,
        "configuration_variable_names_present": sorted(k for k in os.environ if k.startswith("COMFY")),
        "blender_mcp": {"status": "not_verified_by_doctor", "note": "MCP availability must be checked in the calling agent's tool registry; this script only verifies Blender CLI."},
        "readiness": {
            "structural_blender_experiments": tools["blender"].get("python_execution", {}).get("ok", False),
            "image_processing": modules["PIL"]["available"] and modules["numpy"]["available"],
            "godot_cli": tools["godot"]["available"],
            "local_comfy_api": comfy["available"],
            "art_approval": "not_assessed",
            "windows_local_environment": "not_assessed" if platform.system() != "Windows" else "current_host_only",
        },
        "policy": {"downloads_performed": False, "software_upgraded": False,
                   "credentials_collected": False, "workflow_submitted_to_comfyui": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write a UTF-8 JSON report to this path")
    parser.add_argument("--comfy-url", default="http://127.0.0.1:8188",
                        help="Existing local ComfyUI base URL; loopback only")
    args = parser.parse_args()
    try:
        report = collect(args.comfy_url)
    except ValueError as error:
        parser.error(str(error))
    content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
        print(f"Environment report written: {args.output}")
        print(json.dumps(report["readiness"], ensure_ascii=False, indent=2))
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
