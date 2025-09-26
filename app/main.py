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
   
def genarate_pr_description(repo, head, base):
    try:
        comparison = repo.compare(base, head)

        commit_messages = []

        for commit in comparison.commits:
            # get commit massages for create the description
            commit_messages.append(commit.commit.message.split('\n')[0])
            
        if not commit_messages:
            return "No unique commits found between the source and base branches."

        commit_history_text = "\n".join(commit_messages)

        # sumarize all the changes done using commit massages
        prompt = (
            "You are a professional technical writer for software development. "
            "Write a concise, release-note-style pull request description based on the following commit messages. "
            "Group similar changes and highlight the main features added or bugs fixed. "
            "Commit Messages:\n\n"
            f"{commit_history_text}"
        )

        ai_response = ai_model.generate_content(prompt)
        return ai_response.text

    except Exception as e:
        print(f"AI description generation failed: {e}")
        return f"An Error Occured"

    
def create_pr(title, repo_name, head, base, installation_id):
    try:
          
        github_app = verify_signature.get_github_app_instance(installation_id)
        if not github_app:
            raise HTTPException(status_code=500, detail="GitHub App authentication failed.")
        
        repo = github_app.get_repo(repo_name)

        pr_body = genarate_pr_description(repo, head, base)

        # creating pr
        pull_request = repo.create_pull(
            title=title,
            body=pr_body,
            head=head, 
            base=base 
        )

        return {
            "message": f"Pull Request opened successfully from {head} to {base}. Description was AI-generated.",
            "pull_request_url": pull_request.html_url
        }

    except Exception as e:
        print(f"Error creating pull request: {e}")
        if "not found" in str(e).lower() or "not exist" in str(e).lower():
             raise HTTPException(status_code=422, detail=f"Source or base branch not found: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create Pull Request: {e}")
    

@app.post('/new-pr')
def new_pull_request(pr_details: scheam.PullRequestDetails):

    owner = pr_details.repo_name.split('/')[0]
    installation_id = verify_signature.get_installation_id(settings.github_app_id, owner)

    return create_pr(
        repo_name=pr_details.repo_name,
        head=pr_details.source_branch,
        title=pr_details.title,
        base=pr_details.base_branch,
        installation_id=installation_id
    )