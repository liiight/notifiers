"""
Helpers for the Homebrew formula in packaging/homebrew/notifiers.rb.

check
    Checks that the formula's resources are exactly the runtime dependencies of notifiers that aren't provided by a
    Homebrew formula the formula depends on, and that each resource satisfies notifiers' version requirements.
    Run with the interpreter the formula uses, so environment markers resolve the same way.

render SDIST OUTPUT
    Writes the formula with ``url`` and ``sha256`` pointing at a local source distribution, to install it in CI.

Usage::

    uv run --with packaging python packaging/homebrew/check_formula.py check
    uv run --with packaging python packaging/homebrew/check_formula.py render dist/notifiers-2.0.0.tar.gz notifiers.rb
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import tomllib
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[2]
FORMULA = Path(__file__).with_name("notifiers.rb")

# Homebrew formulae that provide Python packages, and the packages they bring along
FORMULA_PROVIDES = {
    "certifi": {"certifi"},
    "pydantic": {"pydantic", "pydantic-core", "annotated-types", "typing-extensions", "typing-inspection"},
}

RESOURCE = re.compile(r'resource "(?P<name>[^"]+)" do\s+url "(?P<url>[^"]+)"\s+sha256 "(?P<sha256>[0-9a-f]{64})"', re.MULTILINE)
DEPENDS_ON = re.compile(r'^\s*depends_on "(?P<name>[^"]+)"', re.MULTILINE)


def _version_from_url(url: str) -> str:
    match = re.search(r"/(?P<name>[A-Za-z0-9_.-]+)-(?P<version>[0-9][A-Za-z0-9.]*)\.tar\.gz$", url)
    if not match:
        raise ValueError(f"can't read a version from {url}")
    return match.group("version")


def _locked_runtime_dependencies() -> dict[str, str]:
    """Runtime dependencies of notifiers (direct and transitive) and their versions, from uv.lock"""
    lock = tomllib.loads((ROOT / "uv.lock").read_text())
    packages = {canonicalize_name(p["name"]): p for p in lock["package"]}
    resolved: dict[str, str] = {}
    pending = [canonicalize_name("notifiers")]
    while pending:
        package = packages[pending.pop()]
        for dependency in package.get("dependencies", []):
            marker = dependency.get("marker")
            if marker and not Requirement(f"x; {marker}").marker.evaluate():
                continue
            name = canonicalize_name(dependency["name"])
            if name not in resolved:
                resolved[name] = packages[name]["version"]
                pending.append(name)
    return resolved


def check() -> int:
    formula = FORMULA.read_text()
    resources = {canonicalize_name(m["name"]): m for m in RESOURCE.finditer(formula)}
    formulae = {m["name"] for m in DEPENDS_ON.finditer(formula)}
    provided = {canonicalize_name(p) for name in formulae for p in FORMULA_PROVIDES.get(name, ())}

    runtime = _locked_runtime_dependencies()
    expected = {name for name in runtime if name not in provided}
    errors = []

    missing = expected - set(resources)
    extra = set(resources) - expected
    if missing:
        errors.append(f"missing resources for: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"resources that aren't runtime dependencies: {', '.join(sorted(extra))}")

    # Every resource must satisfy notifiers' own requirements
    requirements = {canonicalize_name(r.name): r for r in map(Requirement, tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["dependencies"])}
    for name, resource in sorted(resources.items()):
        version = _version_from_url(resource["url"])
        requirement = requirements.get(name)
        if requirement and not requirement.specifier.contains(version, prereleases=True):
            errors.append(f"{name} {version} doesn't satisfy notifiers' requirement {requirement}")

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        print("Update the resources in packaging/homebrew/notifiers.rb, e.g. with `brew update-python-resources`", file=sys.stderr)
        return 1
    print(f"formula resources match the runtime dependencies: {', '.join(sorted(expected))}")
    return 0


def render(sdist: Path, output: Path) -> int:
    formula = FORMULA.read_text()
    sha256 = hashlib.sha256(sdist.read_bytes()).hexdigest()
    # Homebrew reads the version from the file name, e.g. notifiers-2.0.0.tar.gz
    formula = re.sub(r'^  url "[^"]+"$', f'  url "file://{sdist.resolve()}"', formula, count=1, flags=re.MULTILINE)
    formula = re.sub(r'^  sha256 "[0-9a-f]{64}"$', f'  sha256 "{sha256}"', formula, count=1, flags=re.MULTILINE)
    output.write_text(formula)
    print(f"rendered {output} for {sdist.name} (sha256 {sha256})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check")
    render_parser = sub.add_parser("render")
    render_parser.add_argument("sdist", type=Path)
    render_parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "check":
        return check()
    return render(args.sdist, args.output)


if __name__ == "__main__":
    sys.exit(main())
