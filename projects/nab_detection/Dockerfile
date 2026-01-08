# Copyright (c) IBM Confidential
# PID 5698-ZOU, 5698-ZUS
# © Copyright IBM Corp. 2025
#

ARG TARGETARCH

# FROM icr.io/z-operations-unite-snapshot/fission/python-env:develop-${TARGETARCH}-latest
FROM icr.io/z-operations-unite-snapshot/fission/python-env:fix-psirts-${TARGETARCH}-latest

USER root

# arguments
# Z AIOps Unite default user id
ARG UID=1001
# Z AIOps Unite default group id
ARG GID=1001

WORKDIR /userfunc

ENV FILE_PATH=/userfunc \
    FUNCTION_NAME=nab_detection.main \
    FUNCTION_UNIQUE_NAME=ap-nab-detection-function

COPY --chown=${UID}:${GID} . /userfunc/

USER ${UID}

WORKDIR /app
