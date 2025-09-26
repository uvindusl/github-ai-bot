from config import settings
from utils.gemini_init import ai_model
from utils import github_init
from fastapi import HTTPException
import re


def create_feature(language, feature, title, repo_name, installation_id):
    try:

        github_app = github_init.get_github_app_instance(installation_id)
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
          
        github_app = github_init.get_github_app_instance(installation_id)
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


def genarate_review(repo, issue_number):
    pr = repo.get_pull(issue_number)
    diff = pr.get_files()
    file_diffs = ""
    for file in diff:
        file_diffs += f"--- {file.filename} ---\n{file.patch}\n\n"

    try:
        prompt = (
            "You are an expert AI coding assistant. Analyze the following code. "
            "Provide a concise, helpful code review focusing on potential bugs, "
            "security vulnerabilities, and style. Format your response in markdown. "
            f"Here is the diff:\n\n{file_diffs}"
        )
        ai_response = ai_model.generate_content(prompt).text
        pr.create_issue_comment(f"### Uvindu AI BOT Code Review\n\n{ai_response}")
        return {'message': 'code review done successfully'}
    except Exception as e:
        pr.create_issue_comment(f'Error with reviewing code')
        return {'message': 'Error in code reviewing'}
    
def merge_pr(repo, issue_number):
    try:
        pr = repo.get_pull(issue_number)
            
        if not pr.mergeable:
            repo.get_issue(issue_number).create_comment("This PR has some conflicts")
            return {"message": "PR not mergeable."}
                
        pr.merge(merge_method='merge', commit_message=f"Merge pull request #{pr.number}")
                
        repo.get_issue(issue_number).create_comment("Pull request merged successfully!")
        return {"message": "PR merged."}
            
    except Exception as e:
            print(f"Error merging PR: {e}")