#!/usr/bin/env bash
set -euo pipefail
if [ "$(id -u)" -ne 0 ]; then echo 'Run as root on the Olamidepanel server.' >&2; exit 1; fi
if [ ! -f /etc/debian_version ]; then echo 'This installer supports Debian/Ubuntu hosts.' >&2; exit 1; fi
apt-get update
apt-get install -y git ansible-core ca-certificates
installer=/opt/effortlesssmiles-installer
if [ -d "$installer/.git" ]; then
  git -C "$installer" pull --ff-only
else
  git clone https://github.com/olamidebello/effortlesssmiles.git "$installer"
fi
exec ansible-playbook -i localhost, -c local "$installer/ansible/deploy-olamidepanel.yml" "$@"
