#!/usr/bin/env bash
function fail() {
  exit 1
}

cleanAndExport() {
  local raw=$1
  local value=$2
  local clean=$(echo $raw | awk '{print toupper($0)}' | sed -e 's/-/_/g')
  printf -v $clean $value
  export $clean
}


# mkdir -p ${HOME}/.kube
# CONFIG_FILE_PATH=/opt/kube/config ./create-config.py > ${HOME}/.kube/config || fail

python3 watch.py
