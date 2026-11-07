"""Export only verified images, without tags, for safe repeatable Docker import."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from ewb_windows import __version__
from ewb_windows.engine import Docker, Engine, RECIPE
from ewb_windows.state import Store


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", default="default")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    docker = Docker(args.context)
    with tempfile.TemporaryDirectory() as private:
        engine = Engine(Store(Path(private)))
        assert engine.recipes == report["recipes"]
    for role, identifier in report["images"].items():
        value = docker.inspect("image", identifier)
        assert value["Architecture"] == "amd64"
        assert value["Config"]["Labels"][RECIPE] == report["recipes"][role]
    args.output.mkdir(parents=True, exist_ok=True)
    filename = f"Egress-Workbench-Runtime-linux-amd64-{__version__}.tar.gz"
    archive = args.output / filename
    process = subprocess.Popen(docker.command("save", *report["images"].values()), stdout=subprocess.PIPE)
    with gzip.open(archive, "wb", compresslevel=1) as stream:
        while data := process.stdout.read(1024 * 1024):
            stream.write(data)
    assert process.wait() == 0
    with archive.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    manifest = {"schema": 1, "version": __version__, "platform": "linux/amd64", "filename": filename, "bytes": archive.stat().st_size, "sha256": digest, "recipes": report["recipes"], "images": report["images"]}
    (args.output / filename.replace(".tar.gz", ".json")).write_text(json.dumps(manifest, indent=2) + "\n")
    (args.output / (filename + ".sha256")).write_text(digest + "  " + filename + "\n")
    print(json.dumps({"filename": filename, "bytes": archive.stat().st_size, "sha256": digest}))


if __name__ == "__main__":
    main()
