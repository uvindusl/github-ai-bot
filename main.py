from fastapi import FastAPI, Request, HTTPException, Header
from typing import Optional
from utils import verify_signature
import re
from github import Github
import scheam
import google.generativeai as genai
from config import settings 

app = FastAPI()


genai.configure(api_key=settings.gemini_api_key)
ai_model = genai.GenerativeModel("gemini-2.5-flash")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post('/newfeature', response_model=scheam.FeatureSuccess)
def new_feature(feature: scheam.Feature):
    owner = feature.repo_name.split('/')[0]
    installation_id = verify_signature.get_installation_id(settings.github_app_id, owner)

    return create_feature(feature.language, feature.feature, feature.title, feature.repo_name, installation_id)

    

def create_feature(language, feature, title, repo_name, installation_id):
    try:

        github_app = verify_signature.get_github_app_instance(installation_id)
        if not github_app:
            raise HTTPException(status_code=500, detail="GitHub App authentication failed.")

        repo = github_app.get_repo(repo_name)

        prompt = f"""
                You are an expert software engineer. Based on the following description,
                write a single {language} code file that implements the feature.
                Only provide the code, without any extra text or markdown code blocks.
                Description: {feature}
                """

        ai_response = ai_model.generate_content(prompt)
        ai_code = ai_response.text

        # Clean up any potential markdown formatting
        ai_code = re.sub(r'```(?:[a-zA-Z]+\n)?(.*?)\n```', r'\1', ai_code, flags=re.DOTALL)

        branch_name = f"uvindu-ai-bot-{title}"
        main_branch = repo.get_branch("main")

        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)

        if language.lower() == "python":
            file_path = f"uvindu-ai-bot-{title}.py"
        elif language.lower() == "javascript":
            file_path = f"uvindu-ai-bot-{title}.js"

        commit_message = f"feat: Add new feature - {feature}"

        repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=ai_code,
                    branch=branch_name
                )
        
        pr_title = f"Feat: AI-generated feature: {feature}"
        pr_body = (
            "This pull request was automatically created by the AI bot.\n\n"
                f"**Feature description:** {feature}\n\n"
                "Please review the changes."
            )
                
        pull_request = repo.create_pull(
                    title=pr_title,
                    body=pr_body,
                    head=branch_name,
                    base="main"
                )
        
        pr_url = pull_request.html_url

        # Return a dictionary that matches the FeatureSuccess model
        return {
            "message": "Feature created, branch pushed, and PR opened.",
            "pull_request_url": pr_url
        }
            
    except Exception as e:
            print(f"Error processing feature creation request: {e}")
            raise HTTPException(status_code=500, detail=str(e))


