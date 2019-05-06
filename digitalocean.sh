#!/usr/bin/env bash
if test "$BASH" = "" || "$BASH" -uc "a=();true \"\${a[@]}\"" 2>/dev/null; then
    # Bash 4.4, Zsh
    set -euo pipefail
else
    # Bash 4.3 and older chokes on empty arrays with set -u.
    set -eo pipefail
fi
shopt -s nullglob globstar
export DEBIAN_FRONTEND=noninteractive


apt -y update
apt -y install python
apt -y install python-pip

pip install -U pip

# also installs docker-compose
snap install docker

apt -y install wget unzip
wget https://github.com/komuw/wiji-benchmarks/archive/master.zip
unzip master.zip

cd wiji-benchmarks-master/
# edit `compose.env` to add neccesary credentials
screen -S wiji
docker-compose up --build
