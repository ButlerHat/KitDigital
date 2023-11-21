# Kit Digital Deploy with Github Actions

Need to create a secret of cloudflare tunnel

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cloudflared-token-kitdigital-prod
  namespace: default
type: Opaque
data:
  token: <TOKEN>
```

# Github Actions

Need to have a runner with 

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: github-runner-role
rules:
- apiGroups: [""]
  resources: ["pods", "pods/exec", "pods/log", "services", "secrets", "serviceaccounts", "nodes", "persistentvolumeclaims"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["rbac.authorization.k8s.io"]
  resources: ["roles", "rolebindings"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

```

and 

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
- apiGroups: [""]
  resources: ["nodes", "persistentvolumes"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["rbac.authorization.k8s.io"]
  resources: ["clusterroles", "clusterrolebindings"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

```