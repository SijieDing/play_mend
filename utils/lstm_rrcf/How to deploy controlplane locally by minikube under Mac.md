# How to deploy controlplane locally by minikube under Mac
This document introduce the steps about installing controlplane-operator under **minikube** running under **MacOS**. <br>

For the installation under rancher is in another repo of controlplane-operator. <br>

## Cconfige colima and minikube
Because our system needs many resources, we suggests having the following resources.
* CPU 14
* Memory 27G
* Disk 500G

Change the colima VM resource by following steps:
* Edit the file ~/.colima/default/colima.yaml with following items and values: <br>
  * cpu: 14
  * memory: 28
  * Disk: 500
* Restart the colima VM by command
  ```
  brew services stop colima
  brew services start colima
  ```

Start minikube by the following cmd
```
minikube start  --disk-size=490GB --cpus=14 --memory='27g' --driver=docker --kubernetes-version=v1.31.7
```
Enable addon for local-path. 
Our opertor under local env has no PV defination, and it use local-path as storageclass in PVC. So we need enable the following addon.
```
minikube addons enable storage-provisioner-rancher
```

## Start the operator
exports a series of envs in the conole. Please read the README.md under the repo.
To start the operator, use the cmd under the root folder of repo controlplane-operator:
```
make deploy
```
May experience about problem of cmd **sed** and **yq**. Please read the README.md under the repo.controlplane-operator
After running the deploy cmd, it will wait at least **20 minutes**.

## How to use this env to verify code without Travis

This environment replies on the building result from Travis. It takes very long time the finish the whole process. Developer can use this env to deploy their code quickly in similar product env. The next content is an example of how to use this env to verify the new algo detection (lstm-rrcf).

* Create docker image for this lstm-rrcf.

Execute the following command to enter minikube docker env. <br>
**Becareful:** Without this cmd, the followed docker commands may executed in other docker env
```
eval $(minikube docker-env)
```
Run two docker builds at the root of the folder
```
docker build -t nab-demo:latest -f utils/lstm_rrcf/Dockerfile .
docker build -t nab-detection-fission:latest -f utils/lstm_rrcf/Dockerfile_fission .
```

* At the the folder of utils/lstm run the following cmd to deploy this image into this environment
```
kubectl apply -f ap-anomaly-detection-nab-detection-function-deployment.yaml
```
You will see a pod named as ap-anomaly-detection-nab-detection-mock-func-deployment-xxxx being created.

* Now we can mimic router sending traffic to this pod by port forward and postman (or curl)
Run the following cmd to enable port forward
```
kubectl port-forward pod/ap-anomaly-detection-nab-detection-mock-func-deployment-xxxx -n controlplan 8888
```
We changed the log level to info in the deployment. So we can see more detail logs in the pod
```
[WARNING]: Received event is too old. Current time = 2025-09-19 00:23:32.228263, rec_time = 2025-01-01 02:00:00
WARNING:absl:Compiled the loaded model, but the compiled metrics have yet to be built. `model.compile_metrics` will be empty until you train or evaluate the model.
2025-09-19 00:23:32,357 aiops_nab_detection.lstm_rrcf (lstm_rrcf.py:418) [INFO]: Load lstm model from the file /userfunc/aiops_nab_detection/good_40_r1_0.7_finetune1.h5
2025-09-19 00:23:32,367 aiops_nab_detection.redis_utils (redis_utils.py:55) [INFO]: Connected to Redis successfully on attempt 5
INFO:aiops_nab_detection.redis_utils:Connected to Redis successfully on attempt 5
2025-09-19 00:23:32,369 aiops_nab_detection.nab_detection_implment (nab_detection_implment.py:60) [INFO]: Handle metric event loop started, waiting for events...
```
If we write complex testing script call the api to send different events, we can do different testing. At least now we can see there is no problem to start eventloop, connection to redis and other initilization work.

# Remove the env
Just run cmd in the controlplane-operator:
```
kubectl delete deployment ap-anomaly-detection-nab-detection-mock-func-deployment -n controlplane
make clean-all
```