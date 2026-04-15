# Acronyms & Abbreviations

| Acronym | Full Name | Context |
|---|---|---|
| **AG** | Attorney General | BC Ministry of Attorney General — the owning organization of this repo |
| **AKO** | AVI Kubernetes Operator | VMware operator that manages AVI load balancer resources inside Kubernetes/OpenShift |
| **API** | Application Programming Interface | General; also used in context of Kubernetes resource APIs (e.g. `apps/v1`) |
| **AVI** | AVI Networks (VMware) | Load balancer platform; Routes and Ingresses must carry an `aviinfrasetting.ako.vmware.com/name` annotation |
| **BC** | British Columbia | Province; parent jurisdiction for bcgov/bcgov-c GitHub orgs |
| **bcgov-c** | BC Government (confidential) | GitHub organization hosting this repo and its GHCR packages |
| **CD** | Continuous Delivery / Continuous Deployment | The pipeline stage that renders manifests, runs policy checks, and deploys to the cluster |
| **CI** | Continuous Integration | The pipeline stage that builds, tests, and packages application code |
| **CIDR** | Classless Inter-Domain Routing | Notation for IP address ranges used in NetworkPolicy `ipBlock` rules (e.g. `10.0.0.0/8`) |
| **CLI** | Command-Line Interface | e.g. `helm`, `datree`, `polaris`, `kube-linter`, `conftest` |
| **CNI** | Container Network Interface | Kubernetes networking plugin; determines whether NetworkPolicy is enforced (e.g. Calico, OVN-Kubernetes) |
| **EF** | Entity Framework | .NET ORM; `dotnet-8-ef.yml` generates EF migration scripts in CI |
| **GHCR** | GitHub Container Registry | OCI registry at `ghcr.io` used to host both the Helm library chart and app container images |
| **GitOps** | Git Operations | Practice of using Git as the source of truth for deployments; CD pipelines in this repo follow GitOps principles |
| **gRPC** | Google Remote Procedure Call | Protocol buffer-based RPC; `dotnet-8-build-grpc.yml` installs `protoc` for gRPC builds |
| **HPA** | Horizontal Pod Autoscaler | Kubernetes resource (`autoscaling/v2`) that scales pod replicas based on CPU/memory metrics |
| **HTTP(S)** | HyperText Transfer Protocol (Secure) | Application layer protocol; ports 80 (HTTP) and 443 (HTTPS) appear frequently in NetworkPolicy rules |
| **ISB** | Information Security Branch | BC Government branch; `isb.gov.bc.ca/edge-termination-approval` annotation required for edge-terminated Routes |
| **NP** | NetworkPolicy | Shorthand for `networking.k8s.io/v1 NetworkPolicy`; the primary security control for pod-level traffic in this repo |
| **OCI** | Open Container Initiative | Standard for container images and registries; Helm charts are distributed as OCI artifacts via GHCR |
| **OCP** | OpenShift Container Platform | Red Hat's Kubernetes distribution; the target deployment platform for AG applications |
| **OPA** | Open Policy Agent | Policy engine used by Conftest to evaluate Rego rules against rendered Kubernetes manifests |
| **ORM** | Object-Relational Mapper | e.g. Entity Framework for .NET database access |
| **PDB** | Pod Disruption Budget | Kubernetes resource (`policy/v1`) that limits voluntary pod disruptions during maintenance or rolling updates |
| **PR** | Pull Request | GitHub mechanism for proposing and reviewing code changes before merge |
| **PVC** | Persistent Volume Claim | Kubernetes resource (`v1`) that requests durable storage for stateful workloads (e.g. databases) |
| **RBAC** | Role-Based Access Control | Kubernetes authorization mechanism; `kube-linter` checks for default service account misuse |
| **Rego** | Rego (policy language) | Declarative language used by OPA/Conftest; policy files live in `cd/policies/*.rego` |
| **SA** | Service Account | Kubernetes `v1 ServiceAccount`; provided via `ag-template.serviceaccount` |
| **SCC** | Security Context Constraint | OpenShift-specific resource that controls pod security; when `global.openshift: true`, the library omits `runAsUser`/`runAsGroup` so SCC can assign them at runtime |
| **SHA** | Secure Hash Algorithm | Used in image digest pinning (e.g. `image@sha256:...`); preferred over mutable tags |
| **TCP** | Transmission Control Protocol | Transport layer protocol; used explicitly in NetworkPolicy port definitions (e.g. `protocol: TCP`) |
| **TLS** | Transport Layer Security | Encryption protocol for HTTPS; Polaris checks for `tlsSettingsMissing` on exposed resources |
| **YAML** | YAML Ain't Markup Language | File format used for Kubernetes manifests, Helm charts, and GitHub Actions workflows |
