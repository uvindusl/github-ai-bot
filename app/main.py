from fastapi import FastAPI, Request, Header, HTTPException, status
from utils import github_init
import scheam
from config import settings 
from .service import create_feature, create_pr, genarate_review
from typing import Optional

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post('/newfeatures', response_model=scheam.FeatureSuccess)
def new_feature(feature: scheam.Feature):
    owner = feature.repo_name.split('/')[0]
    installation_id = github_init.get_installation_id(settings.github_app_id, owner)

    return create_feature(feature.language, feature.feature, feature.title, feature.repo_name, installation_id)

@app.post('/pullrequets')
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

@app.post('/webhooks')
async def handle_github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):

    payload_body = await request.body()
    
    if not github_init.verify_signature(payload_body, x_hub_signature_256):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    payload = await request.json()
    

    if x_github_event == "issue_comment" and payload['action'] == "created":
        comment_body = payload['comment']['body']
        installation_id = payload['installation']['id']
        github_client = github_init.get_github_app_instance(installation_id)
        
        if not github_client:
            return {"message": "GitHub authentication failed"}
        
        repo_name = payload['repository']['full_name']
        issue_number = payload['issue']['number']
        repo = github_client.get_repo(repo_name)


        if '/review' in comment_body.lower():
            return genarate_review(repo, issue_number)

    return {'message' : 'webhook received, no action taken'}

