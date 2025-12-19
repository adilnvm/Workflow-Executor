from logger import logger
from tools import check_network_status
from llm_provider import get_llm   # <-- abstraction

llm = get_llm()


def run_workflow(message: str) -> dict:
    logger.info(f"Received message: {message}")

    llm_response = llm.generate(message)
    logger.info(f"LLM response: {llm_response}")

    if llm_response.tool_call:
        tool_name = llm_response.tool_call["name"]
        args = llm_response.tool_call["arguments"]

        logger.info(f"Invoking tool: {tool_name} with args {args}")

        if tool_name == "check_network_status":
            tool_result = check_network_status(**args)

            logger.info(f"Tool result: {tool_result}")

            return {
                "llm_message": llm_response.content,
                "tool_result": tool_result,
                "confidence": llm_response.confidence
            }

    return {
        "llm_message": llm_response.content,
        "confidence": llm_response.confidence
    }
