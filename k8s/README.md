# Deploying to Kubernetes

This gets Shopfront running on a real Kubernetes cluster, publicly reachable on the web —
the same shape your MLOps pipeline will eventually deploy into automatically.

## 0. Choose a cluster

You need an actual VM or cluster with a public IP. The most reliable genuinely-free option:

- **Oracle Cloud "Always Free" tier** — a real VM (not a trial credit), free forever. Create an
  Ubuntu instance, open the relevant ports in its security list (30080, 30500, and 6443 if you
  need remote kubectl access), then install a lightweight Kubernetes distribution on it:
  ```bash
  curl -sfL https://get.k3s.io | sh -
  sudo cat /etc/rancher/k3s/k3s.yaml   # kubeconfig, if you want to kubectl from your laptop
  ```
  k3s gives you a fully real single-node Kubernetes cluster in one command.

- Already have a cluster (GKE/EKS/AKS/DigitalOcean/a university lab cluster)? Skip straight to
  step 2 — just replace NodePort with `type: LoadBalancer` in the two `*-service.yaml` files if
  your provider supports one, and use the LoadBalancer's external IP instead of `VM_PUBLIC_IP`.

## 1. Build and push images to a registry

Kubernetes pulls images from a registry — it can't use images sitting only in your local Docker.
Docker Hub's free tier is enough:

```bash
docker login

cd backend
docker build -t <your-dockerhub-username>/shopfront-backend:latest .
docker push <your-dockerhub-username>/shopfront-backend:latest

cd ../frontend
docker build -t <your-dockerhub-username>/shopfront-frontend:latest .
docker push <your-dockerhub-username>/shopfront-frontend:latest
```

## 2. Fill in the manifests

In `k8s/backend-deployment.yaml`, `k8s/frontend-deployment.yaml`:
- Replace `<YOUR_REGISTRY>/...` with the images you just pushed.
- Replace `<VM_PUBLIC_IP>` with your cluster's actual public IP (both files reference it — it
  needs to match in both places since the frontend calls the backend at that address).

## 3. Create the secret, then apply everything

```bash
kubectl create secret generic shopfront-secrets \
  --from-literal=secret-key=$(python3 -c "import secrets; print(secrets.token_hex(32))")

kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

kubectl get pods -w   # wait for both to reach Running
```

## 4. Open it in a browser

```
http://<VM_PUBLIC_IP>:30080
```

Backend health check: `http://<VM_PUBLIC_IP>:30500/health`

If the frontend loads but API calls fail, open devtools → Network tab first; it's almost always
one of: the security-list/firewall port isn't open, or `API_BASE_URL` /  `FRONTEND_ORIGIN` don't
exactly match the address you're actually using (http vs https, trailing slash, wrong port).

## How this maps onto your MLOps pipeline later

- `k8s/backend-deployment.yaml`'s `resources.requests/limits` are exactly the two blocks your
  `generate_k8s_yaml.py` script (step 12 in your implementation order) will overwrite with the
  ML model's predicted CPU/Memory before each automated deploy — nothing else in this file
  needs to change for that integration.
- `/health` is already wired to both `readinessProbe` and `livenessProbe`, so your monitoring
  agent (step 14) and Kubernetes itself agree on what "healthy" means.
- Once GitHub Actions (step 10) is driving this instead of you running `kubectl apply` by hand,
  the registry push in step 1 above becomes a CI step, and steps 2–3 become templated by your
  pipeline instead of manual edits.
