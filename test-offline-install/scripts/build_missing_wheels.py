import os
import sys
import subprocess
import platform

MISSING_PACKAGES = [
    'jaraco.functools',
    'MarkupSafe',
    'pydantic-core==2.33.2',
    'pyyaml',
]

PACKAGES_DIR = 'packages'

pyver = f"{sys.version_info.major}.{sys.version_info.minor}"
arch = platform.machine()
system = platform.system()
print(f"Detected Python {pyver} on {system} ({arch})")

os.makedirs(PACKAGES_DIR, exist_ok=True)

success = []
failure = []

for pkg in MISSING_PACKAGES:
    print(f"\nBuilding wheel for {pkg}...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'wheel', '--no-deps', '--wheel-dir', PACKAGES_DIR, pkg
        ], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[SUCCESS] Built wheel for {pkg}")
            success.append(pkg)
        else:
            print(f"[FAIL] Could not build wheel for {pkg}")
            print(result.stdout)
            print(result.stderr)
            failure.append(pkg)
    except Exception as e:
        print(f"[ERROR] Exception while building {pkg}: {e}")
        failure.append(pkg)

print("\n--- Build Summary ---")
if success:
    print("Successfully built:", ", ".join(success))
if failure:
    print("Failed to build:", ", ".join(failure))
    print("\nTo fix, try running this script on a different machine or Python version matching the missing wheel's requirements.")
    print("Once all wheels are present in the packages/ directory, re-run the offline installer.")
else:
    print("All missing wheels built successfully!") 