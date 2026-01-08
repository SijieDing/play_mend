#!/bin/sh

# This file is required by fission
echo "=== environments ==="
env | sort
echo

echo "=== python version ==="
python --version

echo "=== [Lead function for Training] Build Started ==="
cp -r ${SRC_PKG} ${DEPLOY_PKG}
echo "=== [Lead function for Training] Build Completed ==="
