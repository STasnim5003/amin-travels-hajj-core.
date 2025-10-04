from pydantic import BaseModel


class RunScriptRequestSchema(BaseModel):
    email: str
    password: str
