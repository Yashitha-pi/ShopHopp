# Running Shopfront from your Windows laptop (Minikube + ngrok)

This runs a real local Kubernetes cluster on your laptop and gives it a real public HTTPS URL
via a tunnel, without needing a cloud account, a static IP, or router configuration.

**Tradeoff to know up front:** this only works while your laptop is on, Docker Desktop and
Minikube are running, and the ngrok terminals stay open. Fine for development and demos; not
"always on" hosting.

## 1. Install prerequisites

Open PowerShell **as Administrator** and run:
```powershell
winget install Docker.DockerDesktop
winget install Kubernetes.minikube
winget install Kubernetes.kubectl
```
Restart your machine if prompted, then **open Docker Desktop once** and make sure it says
"Running" (green) before continuing — Minikube's Docker driver needs it.

Install ngrok:
1. Sign up free at https://ngrok.com
2. Download the Windows build, unzip `ngrok.exe` somewhere on your PATH (or just remember its folder)
3. Get your authtoken from the ngrok dashboard, then run:
```powershell
ngrok config add-authtoken <your-token>
```

## 2. Start Minikube

```powershell
minikube start --driver=docker
```
First run downloads a VM image — takes a few minutes.

## 3. Build the images directly into Minikube's Docker

This skips needing a registry entirely — Minikube can use images from your laptop's own Docker
build cache once you point Docker at it:
```powershell
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

cd shopping_app\backend
docker build -t shopfront-backend:latest .

cd ..\frontend
docker build -t shopfront-frontend:latest .
```
Every new PowerShell window needs that `docker-env` line re-run before building — it's what
routes `docker build` into Minikube instead of your normal Docker Desktop.

## 4. Create the secret and deploy the backend

```powershell
cd ..\..\k8s\local

$key = python -c "import secrets; print(secrets.token_hex(32))"
kubectl create secret generic shopfront-secrets --from-literal=secret-key=$key

kubectl apply -f backend-deployment.yaml -f backend-service.yaml
kubectl get pods -w
```
Wait for the backend pod to show `Running` (Ctrl+C to stop watching).

## 5. Tunnel the backend and note its public URL

```powershell
minikube service shopfront-backend-svc --url
```
This prints a local URL like `http://127.0.0.1:52341` — copy the **port number**. Open a **new**
PowerShell window and run:
```powershell
ngrok http 52341
```
Leave this window open. Copy the `https://....ngrok-free.app` URL it shows — this is your
**backend public URL**.

## 6. Deploy the frontend, then tunnel it too

Back in your original window:
```powershell
kubectl apply -f frontend-deployment.yaml -f frontend-service.yaml
kubectl get pods -w
minikube service shopfront-frontend-svc --url
```
Copy that port number too, then open **another new** PowerShell window:
```powershell
ngrok http <that-port>
```
Copy this second `https://....ngrok-free.app` URL — your **frontend public URL**. You now have
two ngrok windows open — leave both running.

## 7. Point the two services at each other's real URLs

Back in your original window, patch both deployments with the real ngrok URLs
(`kubectl set env` triggers an automatic rolling restart, so this takes effect immediately):
```powershell
kubectl set env deployment/shopfront-backend FRONTEND_ORIGIN=<your-frontend-ngrok-url>
kubectl set env deployment/shopfront-frontend API_BASE_URL=<your-backend-ngrok-url>/api

kubectl get pods -w
```
Wait for both pods to cycle back to `Running`.

## 8. Open it

Visit your **frontend ngrok URL** in a browser — from anywhere, not just your laptop's wifi.

## If you restart ngrok later

Free ngrok URLs change every time you restart the tunnel. If that happens, just re-run step 7
with the new URLs.

## Cleaning up

```powershell
kubectl delete -f frontend-deployment.yaml -f frontend-service.yaml -f backend-deployment.yaml -f backend-service.yaml
minikube stop
```
Then close the ngrok windows (Ctrl+C).
