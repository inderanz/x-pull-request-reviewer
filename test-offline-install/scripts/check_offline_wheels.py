import os
import re

REQUIREMENTS_FILE = 'requirements.txt'
PACKAGES_DIR = 'packages'
PY_VERSIONS = ['3.9', '3.10', '3.11', '3.12', '3.13']
PLATFORMS = ['macosx_11_0_arm64', 'macosx_10_9_x86_64']

# Parse requirements.txt for package names
reqs = []
with open(REQUIREMENTS_FILE) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        pkg = re.split(r'[<>=]', line)[0].replace('_', '-').lower()
        reqs.append(pkg)

# Parse all wheels in packages/
wheels = os.listdir(PACKAGES_DIR)
wheel_info = []
for whl in wheels:
    m = re.match(r'([A-Za-z0-9_.\-]+)-([0-9][^\-]*)-(?:py\d+|cp\d+|py3|cp3\d+|py2.py3|py2|py3|py3\.\d+|cp3\.\d+|py3-none|cp3-none|py3-none-any|cp3-none-any|py2-none-any|py2.py3-none-any|py3-none-any)-(.*)\.whl', whl)
    if m:
        pkg, ver, rest = m.groups()
        pyver = None
        plat = None
        # Try to extract python version and platform
        for v in PY_VERSIONS:
            if f'cp{v.replace(".", "")}' in whl or f'py{v.replace(".", "")}' in whl:
                pyver = v
        for platf in PLATFORMS:
            if platf in whl:
                plat = platf
        wheel_info.append((pkg.replace('_', '-').lower(), pyver, plat, whl))

# Check for missing wheels
missing = []
for req in reqs:
    for pyver in PY_VERSIONS:
        for plat in PLATFORMS:
            found = any(
                (w[0] == req and w[1] == pyver and w[2] == plat)
                or (w[0] == req and w[1] is None and w[2] == plat)  # universal wheel for platform
                or (w[0] == req and w[1] == pyver and w[2] is None) # universal for pyver
                or (w[0] == req and w[1] is None and w[2] is None)  # fully universal
                for w in wheel_info
            )
            if not found:
                missing.append(f'{req} (py{pyver}, {plat})')

if missing:
    print('Missing wheels:')
    for m in missing:
        print('  -', m)
else:
    print('All required wheels are present for all supported Python versions and platforms.') 