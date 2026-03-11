from pydantic import BaseModel


class StatusResponse(BaseModel):
    service: str
    project_name: str
    app_env: str
    api_prefix: str
    features: list[str]
