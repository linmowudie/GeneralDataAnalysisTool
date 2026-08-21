# 部署指南（Docker + minikube）

## 架构

| 镜像 | 内容 | 端口 |
|---|---|---|
| `gdat/backend:1.0.0` | FastAPI 后端（uvicorn 单 worker，源码运行） | 8000 |
| `gdat/frontend:1.0.0` | Vite 构建产物 + nginx（`/api` 反代到后端） | 80 |

请求链路：浏览器 → frontend(nginx) → `/api/*` 反代 → backend-svc:8000。

## 前置条件

- 已安装并启动 minikube（`minikube start`）
- kubectl 指向 minikube（`kubectl config use-context minikube`）
- Windows PowerShell

## 一键部署

```powershell
.\deploy\deploy.ps1
```

脚本会用 `minikube image build` 把两个镜像直接构建进 minikube 集群（无需 registry / push），然后 `kubectl apply -k deploy/k8s`。

访问：`minikube service frontend-svc`（NodePort）。

## 手动步骤

```powershell
# 1. 构建镜像（进入 minikube 内部仓库）
minikube image build -t gdat/backend:1.0.0 -f deploy/docker/backend.Dockerfile .
minikube image build -t gdat/frontend:1.0.0 -f deploy/docker/frontend.Dockerfile .

# 2. 部署
kubectl apply -k deploy/k8s
kubectl rollout status deployment/backend

# 3. 访问
minikube service frontend-svc
```

可选 Ingress（统一域名入口）：

```powershell
minikube addons enable ingress
kubectl apply -f deploy/k8s/ingress.yaml
# 将 gdat.local 指向 minikube ip（Add-Content "$env:windir\System32\drivers\etc\hosts" "$(minikube ip) gdat.local"）
```

## 常用运维命令

```powershell
kubectl get pods -l 'app in (backend,frontend)'
kubectl logs deployment/backend -f
kubectl port-forward svc/backend-svc 8000:8000   # 直连后端调试
kubectl delete -k deploy/k8s                      # 卸载
```

## 关键约束与说明

1. **后端副本数必须为 1**：会话状态与步骤锁是进程内内存态，多副本会破坏会话一致性。
2. **运行期数据**：TempStorage/Logs/ModelOutput/ReportOutput/APIOutput 默认挂 emptyDir，Pod 重建即丢失；需持久化请把 Deployment 中对应 volume 改为 PVC。
3. **镜像版本升级**：改 `deploy/k8s/kustomization.yaml` 的 `images.newTag` 与 Dockerfile 构建 tag 后重新执行部署脚本。
4. **依赖同步**：`deploy/docker/requirements.docker.txt` 需与 `pyproject.toml` 的 dependencies 保持一致。
5. **上传体积**：nginx `client_max_body_size 200m`；Ingress 注解已同步，如有更大文件需同步调整两处。
