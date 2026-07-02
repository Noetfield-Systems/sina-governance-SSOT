#!/usr/bin/env bash
# Back-compat shim — sources brain_mac_env_v1.sh.
# shellcheck source=scripts/brain_mac_env_v1.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/brain_mac_env_v1.sh"
