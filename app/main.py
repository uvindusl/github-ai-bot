from fastapi import FastAPI
from utils import github_init
import scheam
from config import settings 
from .service import create_feature, create_pr

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post('/newfeature', response_model=scheam.FeatureSuccess)
def new_feature(feature: scheam.Feature):
    owner = feature.repo_name.split('/')[0]
    installation_id = github_init.get_installation_id(settings.github_app_id, owner)

    return create_feature(feature.language, feature.feature, feature.title, feature.repo_name, installation_id)

@app.post('/new-pr')
def new_pull_request(pr_details: scheam.PullRequestDetails):

    owner = pr_details.repo_name.split('/')[0]
    installation_id = github_init.get_installation_id(settings.github_app_id, owner)

    return create_pr(
        repo_name=pr_details.repo_name,
        head=pr_details.source_branch,
        title=pr_details.title,
        base=pr_details.base_branch,
        installation_id=installation_id
    )