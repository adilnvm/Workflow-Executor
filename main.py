from fastapi import FastAPI
from schemas import BaseModel
from agent import run_workflow


# --------------------------------------------
from dotenv import load_dotenv
load_dotenv()
# ----------------------------------------------


app = FastAPI()


class UserQuery(BaseModel):
    message: str


class WorkflowResult(BaseModel):
    llm_message: str
    confidence: float
    tool_result: dict | None = None


@app.post("/execute-workflow", response_model=WorkflowResult)
def execute_workflow(query: UserQuery):
    return run_workflow(query.message)
