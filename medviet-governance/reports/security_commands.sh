#!/bin/bash
set -e

# git-secrets
# git secrets --install
# git secrets --register-aws
# git secrets --add 'CCCD[:\s]+\d{12}'
# git secrets --add 'cccd[:\s]+\d{12}'
# git secrets --add 'password\s*=\s*["\'"'"'][^"\'"'"']+["\'"'"']'
# git secrets --add 'secret_key\s*=\s*["\'"'"'][^"\'"'"']+["\'"'"']'
git secrets --scan

# bandit
python3 -m bandit -r src/ -ll
python3 -m bandit -r src/ -f json -o reports/bandit_report.json

# trufflehog
trufflehog git file://. --only-verified
trufflehog git file://. --since-commit HEAD~1 --only-verified
