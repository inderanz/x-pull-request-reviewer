#!/bin/bash
set -e

BIN_DIR="$(dirname "$0")/../bin"
mkdir -p "$BIN_DIR"

# Helper to download and chmod +x
fetch_bin() {
  url="$1"
  out="$2"
  echo "Downloading $out ..."
  curl -L "$url" -o "$BIN_DIR/$out"
  chmod +x "$BIN_DIR/$out"
}

# tflint
fetch_bin "https://github.com/terraform-linters/tflint/releases/latest/download/tflint_darwin_amd64.zip" "tflint.zip"
unzip -o "$BIN_DIR/tflint.zip" -d "$BIN_DIR" && rm "$BIN_DIR/tflint.zip"

# terraform (CLI)
fetch_bin "https://releases.hashicorp.com/terraform/1.8.5/terraform_1.8.5_darwin_amd64.zip" "terraform.zip"
unzip -o "$BIN_DIR/terraform.zip" -d "$BIN_DIR" && rm "$BIN_DIR/terraform.zip"

# yamllint (Python, install in venv)
pip3 install --target="$BIN_DIR/yamllint" yamllint
ln -sf "$BIN_DIR/yamllint/bin/yamllint" "$BIN_DIR/yamllint"
ln -sf "$BIN_DIR/yamllint/bin/yamllint" "$BIN_DIR/yamllint-bin"

# prettier (Node, use npx if node present, else skip)
if command -v node >/dev/null; then
  npm install --prefix "$BIN_DIR/prettier" prettier
  ln -sf "$BIN_DIR/prettier/node_modules/.bin/prettier" "$BIN_DIR/prettier"
else
  echo "[WARN] Node.js not found, skipping prettier."
fi

# black (Python)
pip3 install --target="$BIN_DIR/black" black
ln -sf "$BIN_DIR/black/bin/black" "$BIN_DIR/black"

# flake8 (Python)
pip3 install --target="$BIN_DIR/flake8" flake8
ln -sf "$BIN_DIR/flake8/bin/flake8" "$BIN_DIR/flake8"

# gofmt, golint (Go tools, require Go installed)
if command -v go >/dev/null; then
  go install golang.org/x/lint/golint@latest
  cp "$(go env GOPATH)/bin/golint" "$BIN_DIR/golint"
  ln -sf "$(go env GOPATH)/bin/gofmt" "$BIN_DIR/gofmt"
else
  echo "[WARN] Go not found, skipping gofmt/golint."
fi

# google-java-format
fetch_bin "https://github.com/google/google-java-format/releases/download/v1.21.0/google-java-format-1.21.0-all-deps.jar" "google-java-format.jar"
echo -e '#!/bin/bash\nexec java -jar "$0/../bin/google-java-format.jar" "$@"' > "$BIN_DIR/google-java-format"
chmod +x "$BIN_DIR/google-java-format"

# checkstyle
fetch_bin "https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.12.4/checkstyle-10.12.4-all.jar" "checkstyle.jar"
echo -e '#!/bin/bash\nexec java -jar "$0/../bin/checkstyle.jar" "$@"' > "$BIN_DIR/checkstyle"
chmod +x "$BIN_DIR/checkstyle"

# shfmt
fetch_bin "https://github.com/mvdan/sh/releases/latest/download/shfmt_v3.7.0_darwin_amd64" "shfmt"

# shellcheck
fetch_bin "https://github.com/koalaman/shellcheck/releases/download/v0.9.0/shellcheck-v0.9.0.darwin.x86_64" "shellcheck"

echo "All tools downloaded to $BIN_DIR. Add this to your PATH or let the agent use it directly." 