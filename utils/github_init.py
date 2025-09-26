import hashlib
import hmac
from fastapi import HTTPException
from github import GithubIntegration, Github, Auth
from config import settings


# https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries

def verify_signature(request_body: bytes, signature_header: str):
    if not signature_header:
        return False
    
    sha_name, signature = signature_header.split("=")
    if sha_name != "sha256":
        return False
    
    secret_bytes = settings.github_webhook_secret.encode('utf-8')
    mac = hmac.new(secret_bytes, msg=request_body, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)
    
# Read the private key file
try:
    with open(settings.github_private_key_path, 'r') as key_file:
        github_content = key_file.read() 
except FileNotFoundError:
    raise Exception(f"GitHub private key file not found at {settings.github_private_key_path}")

# function get installation id
def get_installation_id(app_id: int, owner: str) -> int:
    try:
        integration = GithubIntegration(app_id, github_content)

        installations = integration.get_installations()

        for installation in installations:
            if installation.account.login == owner:
                print(f"Found installation ID: {installation.id} for owner: {owner}")
                return installation.id

        raise ValueError(f"No installation found for the owner: {owner}")

    except Exception as e:
        raise Exception(f"Failed to retrieve installation ID: {e}")

# function to authanticate
def get_github_app_instance(installation_id: int):
    try:
        app_auth = Auth.AppAuth(settings.github_app_id, github_content)
        installation_auth = app_auth.get_installation_auth(installation_id)
        return Github(auth=installation_auth)
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None