#!/usr/bin/env bash
if test "$BASH" = "" || "$BASH" -uc "a=();true \"\${a[@]}\"" 2>/dev/null; then
    # Bash 4.4, Zsh
    set -euo pipefail
else
    # Bash 4.3 and older chokes on empty arrays with set -u.
    set -eo pipefail
fi
shopt -s nullglob globstar

export DEBIAN_FRONTEND=noninteractive && \
apt -y update && \
apt -y install python && \
apt -y install python-pip nano wget unzip curl screen

# NB: do not install docker from snap; it is broken
apt -y remove docker docker-engine docker.io containerd runc && \
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
apt-key fingerprint 0EBFCD88 && \
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
apt -y update; apt -y autoremove && \
apt -y install docker-ce && \
usermod -aG docker $(whoami) && \
pip install -U docker-compose

wget https://github.com/komuw/wiji-benchmarks/archive/master.zip && \
unzip master.zip && \
mv wiji-benchmarks-master/ wiji-benchmarks && \
cd wiji-benchmarks/

# edit `compose.env` to add neccesary credentials

screen -dm docker-compose up