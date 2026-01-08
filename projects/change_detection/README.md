# aiops_unite change_detection

## Run locally

### Install dependencies

You need Artifactory access information to pull dependencies. The user ID and token should be stored in `GLOBAL_ZAIOPS_READ_USER_ID` and `GLOBAL_ZAIOPS_READ_USER_TOKEN`.

```
export GLOBAL_ZAIOPS_READ_USER_ID=<artifactory-user-id>
export GLOBAL_ZAIOPS_READ_USER_TOKEN=<artifactory-user-token>
export PYPI_REPO=sys-z-aiops-unite-team-snapshot-pypi-virtual

make requirements
```

### Lint

```
make lint
```

### Start locally

Define `AP_ANOMALY_DETECTION_FUNCTION_CONFIG` variable as location of the config file.

```
export AP_ANOMALY_DETECTION_FUNCTION_CONFIG=/path/to/libs/aiops_unite/sample-config.yaml

python change_detection.py
```

## Test locally with fission

### Prepare fission environment

Follow instructions on [Test locally with fission](https://github.ibm.com/z-aiops-unite/ap-functions/blob/main/ap-time-series-event-function/README.md#test-locally-without-fission)

### Prepare fission deployment specs


```shell
export PROJECT_KEY="ap-aa-$(basename $(pwd) | sed s/_/-/g)-func"
export KAFKA_INPUT_TOPIC=zou.metrics.00.raw
export KAFKA_OUTPUT_TOPIC=jack_change_detection_resp
export KAFKA_ERROR_TOPIC=jack_change_detection_err
fission spec init
fission env create --spec --name ${PROJECT_KEY}-env --image ${CR_REPO}/${CR_NAMESPACE}/fission/python-env:main-amd64-latest --builder ${CR_REPO}/${CR_NAMESPACE}/fission/python-builder:main-amd64-latest --envNamespace ${FISSION_NAMESPACE} --version 3 --poolsize 1 --imagepullsecret ${UNITE_IMAGEPULLSECRET_NAME}
fission package create --spec --name ${PROJECT_KEY}-package --sourcearchive $(find ./ -name '*.zip') --env ${PROJECT_KEY}-env --buildcmd "./scripts/build.sh" --pkgNamespace ${FISSION_NAMESPACE} --envNamespace ${FISSION_NAMESPACE}
fission fn create --spec --name ${PROJECT_KEY} --pkgname ${PROJECT_KEY}-package  --entrypoint "change_detection.main" --fnNamespace ${FISSION_NAMESPACE} --envNamespace ${FISSION_NAMESPACE} --configmap ap-config --fntimeout 900
fission mqt create --spec --name ${PROJECT_KEY}-mqt --function ${PROJECT_KEY} --mqtype kafka --mqtkind fission --topic ${KAFKA_INPUT_TOPIC} --resptopic ${KAFKA_OUTPUT_TOPIC} --errortopic ${KAFKA_ERROR_TOPIC} --fnNamespace ${FISSION_NAMESPACE} --maxreplicacount 1
```

Modify file `specs/env-ap-aa-change-detection-func-env.yaml` `runtime.container.env` section to define environment variable `AP_ANOMALY_DETECTION_FUNCTION_CONFIG`:

```yaml
runtime:
  container:
    name: ""
    resources: {}
    env:
      - name: AP_ANOMALY_DETECTION_FUNCTION_CONFIG
        value: /configs/fission/ap-config/ap-aa-config.yaml
```
