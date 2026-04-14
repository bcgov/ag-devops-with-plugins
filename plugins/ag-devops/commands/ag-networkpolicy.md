---
description: "Guide writing a compliant NetworkPolicy for OpenShift Emerald using ag-template.networkpolicy intent inputs. Covers service-to-service, router ingress, database egress, and internet egress approval patterns."
---

Use the `author-networkpolicy` skill to write a compliant NetworkPolicy for the specified workload.

Ask the developer:
1. Which workload is this policy for?
2. Does this workload have an OpenShift Route (needs router ingress)?
3. What other services call into this workload, and on which port?
4. What does this workload call out to (other services, database, external CIDR)?
5. Does it need internet-wide egress (`0.0.0.0/0`)? If so, what is the justification and approver?

Then generate the complete `ag-template.networkpolicy` template block using intent inputs (`AllowIngressFrom` / `AllowEgressTo`).

Warn the developer if any pattern would be denied by Conftest (missing peers, missing ports, or unapproved internet egress).
