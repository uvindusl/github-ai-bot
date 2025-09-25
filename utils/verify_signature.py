import hashlib
import hmac
from fastapi import HTTPException
from github import GithubIntegration, Github, Auth
from config import settings


# https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries

def verify_signature(payload_body, secret_token, signature_header):
    if not signature_header:
        raise HTTPException(status_code=403, detail="x-hub-signature-256 header is missing!")
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")
    
# Read the private key file ONCE and store its content as a string
try:
    with open(settings.github_private_key_path, 'r') as key_file:
        github_content = key_file.read() 
except FileNotFoundError:
    raise Exception(f"GitHub private key file not found at {settings.github_private_key_path}")

def get_installation_id(app_id: int, owner: str) -> int:
    """
    Retrieves the installation ID for a given app ID and owner (user or organization).
    """
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
    """
    Creates an authenticated GitHub instance for a specific repository installation.
    """
    try:
        app_auth = Auth.AppAuth(settings.github_app_id, github_content)
        installation_auth = app_auth.get_installation_auth(installation_id)
        return Github(auth=installation_auth)
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None