# GitHub AI Assistant Bot

This project implements a GitHub App written in Python using **FastAPI** and **PyGithub**. It integrates the **Gemini API** to provide advanced code review and feature generation capabilities directly through issue or pull request comments. It also includes a command-line interface (CLI) for manual bot interaction.

-----

## Features

This bot responds to comments in GitHub Issues and Pull Requests with the following commands:

| Command | Description | Location | Permissions Needed |
| :--- | :--- | :--- | :--- |
| **`/review`** | Generates an AI-powered code review for the latest diff in the Pull Request. | Pull Request | Read: Pull requests |
| **`/create-feature 'description'`** | Instructs the AI to generate code for a new feature, then creates a new branch, commits the file, and opens a Pull Request. | Issue or PR | Read & Write: Contents, Pull requests |
| **`/merge`** | Attempts to merge the current Pull Request (if mergeable, passes checks, and is approved). | Pull Request | Read & Write: Pull requests |

-----

## Setup and Installation

Follow these steps to get your GitHub App running locally.

### 1\. Prerequisites

You must have the following installed:

  * **Python 3.8+**
  * **A Gemini API Key** (from Google AI Studio)
  * **A GitHub App** (created on GitHub)
  * **Node.js/npm** (to install `smee-client` for local tunneling)

### 2\. Create the GitHub App

1.  Go to **Settings** $\rightarrow$ **Developer settings** $\rightarrow$ **GitHub Apps**.
2.  **Permissions & events** configuration:
      * Set **Contents** to **Read and write**.
      * Set **Issues** to **Read and write**.
      * Set **Pull requests** to **Read and write**.
      * Subscribe to **Issue comments** and **Pull request** events.
3.  Download the **Private Key** (`.pem` file) and save its path.
4.  Note the **App ID**.
5.  Go to **Install App** and install it on your target repository. Note the **Installation ID** from the resulting URL.
6.  Set the **Webhook URL** to your unique `smee.io` URL (e.g., `https://smee.io/your-unique-url`).
7.  Set the **Webhook Secret** (a strong, random string).

### 3\. Project Setup

1.  Clone this repository and navigate into the directory.
2.  Create and activate a virtual environment.
3.  Install dependencies:
    ```bash
    pip install fastapi uvicorn python-dotenv PyGithub google-generativeai
    ```
4.  Create a file named **`.env`** and populate it with your keys:
    ```env
    # GitHub App Credentials
    GITHUB_APP_ID="[Your App ID]"
    GITHUB_WEBHOOK_SECRET="[Your Webhook Secret]"

    # Path to the downloaded .pem file
    GITHUB_PRIVATE_KEY_PATH="/home/uvindu/Documents/github-ai-bot/uvindu-ai-bot.2025-09-25.private-key.pem"

    # Gemini API Key
    GEMINI_API_KEY="[Your Gemini API Key]"
    ```
5.  Save your bot code as **`bot.py`**.

### 4\. Running the Bot

You will need two terminal windows: one for the secure tunnel and one for the FastAPI server.

#### Terminal 1: Start Smee Tunnel

This tunnels webhooks from GitHub to your local machine.

```bash
# Install smee client if you haven't already
npm install -g smee-client

# Run the client, replacing the URL with your Smee URL
smee -u https://smee.io/your-unique-url -t http://localhost:8000/github-webhook/
```

#### Terminal 2: Start FastAPI Server

This runs your Python bot script.

```bash
uvicorn bot:app --reload
```

The bot is now ready to receive commands\!

-----

## Usage (GitHub & CLI)

### 1\. Interacting via GitHub Comments (Recommended)

Simply post a comment in an Issue or Pull Request:

```
/create-feature "A Python function to calculate the factorial of a number."
```

### 2\. Interacting via Command Line (For Testing/Debugging)

To use the powerful CLI, ensure your `cli.py` file (with the CLI logic) is in the same directory. You'll need the **repository name** (e.g., `octocat/Spoon-Knife`) and the **Installation ID**.

| Action | Command |
| :--- | :--- |
| **Review a PR** | `python cli.py --repo "user/repo" --issue 5 --install_id 12345 --command review` |
| **Create a Feature** | `python cli.py --repo "user/repo" --issue 1 --install_id 12345 --command create-feature --desc "a helper function"` |
| **Merge a PR** | `python cli.py --repo "user/repo" --issue 5 --install_id 12345 --command merge` |
