from pydantic import BaseModel

class Feature(BaseModel):
    language: str
    feature: str
    title: str
    repo_name: str

class FeatureSuccess(BaseModel):
    message: str
    pull_request_url: str


class PullRequestDetails(BaseModel):
    repo_name: str
    source_branch: str
    title: str
    base_branch: str