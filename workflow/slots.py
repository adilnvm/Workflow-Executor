WORKFLOW_SLOTS = {
    "network_troubleshooting_workflow": {
        "required": ["issue_type", "service_type"],
        "questions": {
            "issue_type": "Are you facing slow internet, no signal, or call drops?",
            "service_type": "Is this issue on mobile data or JioFiber?"
        }
    },

    "billing_explanation_workflow": {
        "required": ["account_type"],
        "questions": {
            "account_type": "Is your connection prepaid or postpaid?"
        }
    }
}
