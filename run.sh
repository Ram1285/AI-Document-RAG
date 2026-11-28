#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

if [[ -x ".venv/bin/python" ]]; then
  python_cmd=".venv/bin/python"
elif [[ -x ".venv/Scripts/python.exe" ]]; then
  python_cmd=".venv/Scripts/python.exe"
else
  python_cmd="python"
fi

exec "$python_cmd" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
