import click
from utils import send_request

@click.group()
def cli():
    pass

@cli.command()
@click.option('--repo-name', required=True, help='Full repository name (e.g., owner/repository).')
@click.option('--title', required=True, help='Title for the new feature or task.')
@click.option('--language', required=True, help='The primary programming language of the feature (e.g., Python, JavaScript).')
@click.option('--description', 'feature_desc', required=True, help='Detailed description of the feature to be created.')
def feature(repo_name: str, title: str, language: str, feature_desc: str):

    data = {
        "repo_name": repo_name,
        "title": title,
        "language": language,
        "feature": feature_desc
    }
    
    send_request("newfeatures", data)


@cli.command()
@click.option('--repo-name', required=True, help='Full repository name (e.g., owner/repository).')
@click.option('--title', required=True, help='Title for the new Pull Request.')
@click.option('--source', required=True, help='The branch containing the changes (head).')
@click.option('--base', required=True, help='The branch to merge into (base, typically main/master).')
def pr(repo_name: str, title: str, source: str, base: str):
    
    data = {
        "repo_name": repo_name,
        "title": title,
        "source_branch": source,
        "base_branch": base
    }
    
    send_request("pullrequets", data)


if __name__ == '__main__':
    cli()