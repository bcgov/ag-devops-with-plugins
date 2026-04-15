CHART_PATH    := ./gitops
ENV           ?= dev
RELEASE       := @@PROJECT@@
AG_DEVOPS_ROOT ?= ag-devops

.PHONY: deps render validate lint deploy

deps:
	helm dependency update $(CHART_PATH)

render: deps
	helm template $(RELEASE) $(CHART_PATH) \
	  --values $(CHART_PATH)/values.yaml \
	  --values $(CHART_PATH)/values-$(ENV).yaml \
	  > rendered.yaml

validate: render
	datree test rendered.yaml --policy-config $(AG_DEVOPS_ROOT)/cd/policies/datree-policies.yaml
	polaris audit --config $(AG_DEVOPS_ROOT)/cd/policies/polaris.yaml --format pretty rendered.yaml
	kube-linter lint rendered.yaml --config $(AG_DEVOPS_ROOT)/cd/policies/kube-linter.yaml
	conftest test rendered.yaml --policy $(AG_DEVOPS_ROOT)/cd/policies --all-namespaces --fail-on-warn

lint:
	helm lint $(CHART_PATH) \
	  --values $(CHART_PATH)/values.yaml \
	  --values $(CHART_PATH)/values-$(ENV).yaml

deploy: validate
	helm upgrade --install $(RELEASE) $(CHART_PATH) \
	  --values $(CHART_PATH)/values.yaml \
	  --values $(CHART_PATH)/values-$(ENV).yaml \
	  --namespace @@NAMESPACE_DEV@@ \
	  --wait --timeout 5m

# Override AG_DEVOPS_ROOT if ag-devops is installed elsewhere:
#   make validate AG_DEVOPS_ROOT=/path/to/ag-devops
# Or if using the marketplace plugin install (~/.claude/plugins/ag-devops):
#   make validate AG_DEVOPS_ROOT=~/.claude/plugins/ag-devops
