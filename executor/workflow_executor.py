from tools.network import (
    validate_region,
    check_network_status,
    suggest_resolution
)

STEP_HANDLERS = {
    "validate_region": validate_region,
    "check_network_status": check_network_status,
    "suggest_resolution": suggest_resolution
}

def execute_workflow(workflow: dict, context: dict) -> dict:
    results = []

    for step in workflow["steps"]:
        handler = STEP_HANDLERS[step]

        if step == "validate_region":
            region = context.get("region", "unknown")
            output = handler(region)

            if not output["valid"]:
                return {
                    "status": "needs_info",
                    "message": output["message"],
                    "steps": results
                }

        elif step == "check_network_status":
            region = context.get("region", "unknown")
            output = handler(region)
            context["status"] = output["status"]

        elif step == "suggest_resolution":
            output = handler(context["status"])

        results.append({step: output})

    return {
        "status": "resolved",
        "steps": results
    }
