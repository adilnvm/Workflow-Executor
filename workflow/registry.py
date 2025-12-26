from workflow.network_workflow import network_troubleshooting_workflow
from workflow.billing_workflow import billing_explanation_workflow

WORKFLOW_REGISTRY = {
    "network_troubleshooting_workflow": network_troubleshooting_workflow,
    "billing_explanation_workflow": billing_explanation_workflow,
    "recharge_resolution_workflow": None,
    "sim_device_troubleshooting_workflow": None,
}
