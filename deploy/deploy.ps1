# 一键构建镜像（进入 minikube 内部镜像仓库）并部署到 minikube
# 用法：在仓库根目录执行  .\deploy\deploy.ps1 [-SkipBuild]

param(
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

$BackendImage = "gdat/backend:1.0.0"
$FrontendImage = "gdat/frontend:1.0.0"

# 确保构建在 minikube 的 docker 环境中进行（镜像直接进集群，无需 push）
if (-not $SkipBuild) {
    Write-Host "==> 构建后端镜像 $BackendImage" -ForegroundColor Cyan
    minikube image build -t $BackendImage -f deploy/docker/backend.Dockerfile .
    if ($LASTEXITCODE -ne 0) { throw "后端镜像构建失败" }

    Write-Host "==> 构建前端镜像 $FrontendImage" -ForegroundColor Cyan
    minikube image build -t $FrontendImage -f deploy/docker/frontend.Dockerfile .
    if ($LASTEXITCODE -ne 0) { throw "前端镜像构建失败" }
}

Write-Host "==> 应用 k8s 清单" -ForegroundColor Cyan
kubectl apply -k deploy/k8s

Write-Host "==> 等待后端就绪" -ForegroundColor Cyan
kubectl rollout status deployment/backend --timeout=180s
kubectl rollout status deployment/frontend --timeout=120s

Write-Host "==> Pod 状态" -ForegroundColor Cyan
kubectl get pods -l 'app in (backend,frontend)' -o wide

Write-Host ""
Write-Host "部署完成。访问前端：" -ForegroundColor Green
Write-Host "  minikube service frontend-svc"
Write-Host "（可选 Ingress：minikube addons enable ingress; kubectl apply -f deploy/k8s/ingress.yaml）"
