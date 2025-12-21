from dotenv import load_dotenv
load_dotenv()




from fastapi import FastAPI
from fastapi import Body
from pydantic import BaseModel
from agent import run_workflow
from schemas.requests import UserQuery
print("DEBUG UserQuery annotations:", UserQuery.model_fields)


app = FastAPI()


# class UserQuery(BaseModel):
#     message: str
#     ticket_id: str


# hi if someone's reading this(highly unlikely though),
# i wrote some shitty code here ;]
# sorry
    
class WorkflowResponse(BaseModel):
    summary: str
    workflow_result: dict
    confidence: float





@app.post("/execute-workflow")
def execute(query: UserQuery):
    return run_workflow(
        message=query.message,
        ticket_id=query.ticket_id
    )
