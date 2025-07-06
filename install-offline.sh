# At the end of the script, print usage instructions
cat <<EOF

============================================================
✅ XPRR Agent installation complete!

To get started:
  1. Activate your environment:
     source venv/bin/activate
  2. See available commands:
     xprr --help
  3. Run a review (examples):
     xprr review --pr <PR_URL>
     xprr review --repo <local_repo_path>

For more options, run:
  xprr review --help

============================================================
EOF 