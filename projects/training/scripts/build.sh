#!/bin/sh

# This file is required by fission
echo "=== environments ==="
env | sort
echo

echo "=== python version ==="
python --version

echo "=== [Training Function] Build Started ==="
cp -r ${SRC_PKG} ${DEPLOY_PKG}
echo "=== [Training Function] Build Completed ==="
