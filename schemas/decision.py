from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Annotated


class Decision(BaseModel):
    intent: Literal[
        "network_issue",
        "slow_internet",
        "no_signal",
        "call_drop",
        "billing_issue",
        "unexpected_charges",
        "recharge_issue",
        "plan_validity",
        "sim_issue",
        "device_issue",
        "unknown"
    ]

    confidence: Annotated[float, Field(ge=0.0, le=1.0)]

    entities: Dict[str, str] = Field(default_factory=dict)

    workflow: Literal[
        "network_troubleshooting_workflow",
        "billing_explanation_workflow",
        "recharge_resolution_workflow",
        "sim_device_troubleshooting_workflow",
        "clarification_workflow"
    ]

    next_action: Literal[
        "execute_workflow",
        "ask_clarification",
        "escalate"
    ]

    clarification_question: Optional[str] = None
