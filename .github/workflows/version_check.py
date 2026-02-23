import re
import toml
import requests
import sys
from pathlib import Path
import os
from packaging import version

package = "alpha-mini-rug"
error_code = []


def main():
    # ==========================================================================
    tag_version = os.environ.get('CHECK_RELEASE_TAG')
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        tag_version = "0.7.3.4"  # for testing

    if not tag_version:
        print("No release tag provided")
        tag_version = "NO_TAG"
        error_code.append("github tag is missing")

    print(f"Release tag   : {tag_version}")

    # ==========================================================================
    pyproject_path = Path("alpha-mini-rug/pyproject.toml")
    if pyproject_path.is_file():
        data = toml.loads(pyproject_path.read_text())
        try:
            pyproject_version = data["project"]["version"]
        except Exception as e:
            pyproject_version = "NOT_FOUND"
            print(f"pyproject.toml error: {e}")
    else:
        pyproject_version = "MISSING_FILE"

    if pyproject_version != tag_version:
        error_code.append("pyproject.toml is not the same as tag")

    print(f"pyproject.toml: {pyproject_version}")

    # ==========================================================================
    setup_py_path = Path("alpha-mini-rug/setup.py")
    if setup_py_path.is_file():
        try:
            with open(setup_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(
                r"version[=:]\s*['\"]([^'\"]*)['\"]", content, re.IGNORECASE)
            if match:
                setup_version = match.group(1)
            else:
                setup_version = "NO_VERSION_FOUND"
        except Exception as e:
            setup_version = "ERROR"
            print(f"setup.py error: {e}")
    else:
        setup_version = "MISSING_FILE"

    if setup_version != tag_version:
        error_code.append("setup.py is not the same as tag")

    if setup_version != pyproject_version:
        error_code.append("setup.py is not the same as pyproject.toml")

    print(f"setup.py      : {setup_version}")

    # ==========================================================================
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:
        print(f"PyPI request failed: {e}", file=sys.stderr)
        error_code.append("pypi")

    if resp.status_code == 200:
        pypi_info = resp.json()
        pipy_all_releases = pypi_info.get("releases", {}).keys()

        # print(pypi_info.get("releases", {}))
        pypi_version = pypi_info.get("info", {}).get("version", "")
    elif resp.status_code == 404:
        pypi_version = "html: 404"  # not published yet
    else:
        print(f"PyPI request failed: {resp.status_code}", file=sys.stderr)
        pypi_version = "html: 400"
        # Add this import at the top of your file, then use this comparison:

    if pypi_version == tag_version:
        error_code.append("pypi last is the same")

    if tag_version in pipy_all_releases:
        error_code.append("pypi version is in releases")
        print(f"PyPI releases: {pipy_all_releases or '<none>'}")

    try:
        if version.parse(tag_version) <= version.parse(pypi_version):
            error_code.append("tag version is not higher than pypi version")
    except Exception as e:
        print(f"Version comparison error: {e}", file=sys.stderr)
        error_code.append("version comparison failed")

    print(f"PyPI latest   : {pypi_version or '<none>'}")

    # ==========================================================================

    gh_out_path = Path("${GITHUB_OUTPUT}")

    # try:
    #     with gh_out_path.open("a") as f:
    #         f.write(f"release_ok={'true' if not error_code else 'false'}\n")
    #         f.write(f"setup_version={setup_version}\n")
    #         f.write(f"tag_version={tag_version}\n")
    #         f.write(f"pyproject_version={pyproject_version}\n")
    #         f.write(f"pypi_version={pypi_version}\n")
    #         f.write(f"error_code={','.join(error_code)}\n")
    # except Exception as e:
    #     print(f"Failed writing GITHUB_OUTPUT: {e}", file=sys.stderr)
    #     sys.exit(1)

    if not error_code:
        print("Approved release number")
    else:
        print("\n\rRelease numbers are not in sync\n\r", file=sys.stderr)
        # print(f"Errors in: {', '.join(error_code)}", file=sys.stderr)
        for error in error_code:
            print(f"error in: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
