#!/usr/bin/env python3
"""
Simple script to check if GitHub repositories are private or public.
Usage: python check_repo_privacy.py <owner/repo> [<owner/repo> ...]
       python check_repo_privacy.py --user <username>  (lists all accessible repos for a user)
Example: python check_repo_privacy.py evi-kopadi/nemo
         python check_repo_privacy.py --user evi-kopadi

Set GITHUB_TOKEN environment variable for authentication if needed.
"""

import sys
import urllib.request
import json
import os


def list_user_repos(username, token=None):
    """
    List all repositories for a given user.
    
    Args:
        username: GitHub username
        token: Optional GitHub personal access token
    
    Returns:
        list: List of repository information dictionaries
    """
    api_url = f"https://api.github.com/users/{username}/repos?per_page=100"
    
    try:
        request = urllib.request.Request(api_url)
        request.add_header('Accept', 'application/vnd.github+json')
        
        if token:
            request.add_header('Authorization', f'Bearer {token}')
        
        with urllib.request.urlopen(request) as response:
            repos = json.loads(response.read().decode())
            return [{
                'name': repo['full_name'],
                'private': repo['private'],
                'visibility': repo.get('visibility', 'unknown'),
                'description': repo.get('description', 'No description'),
                'url': repo['html_url']
            } for repo in repos]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: User '{username}' not found")
        elif e.code == 403:
            print(f"Error: Access forbidden. Try setting GITHUB_TOKEN environment variable.")
        else:
            print(f"Error: HTTP {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def check_repo_privacy(owner, repo, token=None):
    """
    Check if a GitHub repository is private or public.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        token: Optional GitHub personal access token
    
    Returns:
        dict: Repository information including privacy status
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    
    try:
        request = urllib.request.Request(api_url)
        request.add_header('Accept', 'application/vnd.github+json')
        
        # Add authentication if token is provided
        if token:
            request.add_header('Authorization', f'Bearer {token}')
        
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())
            return {
                'name': data['full_name'],
                'private': data['private'],
                'visibility': data.get('visibility', 'unknown'),
                'description': data.get('description', 'No description'),
                'url': data['html_url']
            }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {
                'name': f"{owner}/{repo}",
                'error': 'Repository not found or not accessible'
            }
        elif e.code == 403:
            return {
                'name': f"{owner}/{repo}",
                'error': 'Access forbidden. Try setting GITHUB_TOKEN environment variable.'
            }
        else:
            return {
                'name': f"{owner}/{repo}",
                'error': f'HTTP Error {e.code}: {e.reason}'
            }
    except Exception as e:
        return {
            'name': f"{owner}/{repo}",
            'error': str(e)
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_repo_privacy.py <owner/repo> [<owner/repo> ...]")
        print("       python check_repo_privacy.py --user <username>")
        print("Example: python check_repo_privacy.py evi-kopadi/nemo")
        print("         python check_repo_privacy.py --user evi-kopadi")
        print("\nSet GITHUB_TOKEN environment variable for authentication if needed.")
        sys.exit(1)
    
    # Check for GitHub token in environment
    github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    
    if github_token:
        print("Using GitHub authentication token.\n")
    else:
        print("No GitHub token found. Checking public repositories only.\n")
    
    # Handle --user flag to list all repos for a user
    if sys.argv[1] == '--user':
        if len(sys.argv) < 3:
            print("Error: --user flag requires a username")
            sys.exit(1)
        
        username = sys.argv[2]
        print(f"Fetching repositories for user: {username}\n")
        
        repos = list_user_repos(username, github_token)
        
        if not repos:
            print("No repositories found or accessible.")
            return
        
        print(f"Found {len(repos)} repositories:\n")
        
        private_count = sum(1 for r in repos if r['private'])
        public_count = len(repos) - private_count
        
        for info in repos:
            privacy_status = "🔒 PRIVATE" if info['private'] else "🌐 PUBLIC"
            print(f"Repository: {info['name']}")
            print(f"Privacy: {privacy_status}")
            print(f"Visibility: {info['visibility']}")
            print(f"Description: {info['description']}")
            print(f"URL: {info['url']}\n")
        
        print(f"Summary: {public_count} public, {private_count} private")
        return
    
    # Normal mode: check specific repos
    repos = sys.argv[1:]
    
    print("Checking repository privacy status...\n")
    
    for repo_spec in repos:
        if '/' not in repo_spec:
            print(f"Error: Invalid repository format '{repo_spec}'. Use 'owner/repo' format.\n")
            continue
        
        owner, repo = repo_spec.split('/', 1)
        info = check_repo_privacy(owner, repo, github_token)
        
        if 'error' in info:
            print(f"Repository: {info['name']}")
            print(f"Status: ❌ {info['error']}\n")
        else:
            privacy_status = "🔒 PRIVATE" if info['private'] else "🌐 PUBLIC"
            print(f"Repository: {info['name']}")
            print(f"Privacy: {privacy_status}")
            print(f"Visibility: {info['visibility']}")
            print(f"Description: {info['description']}")
            print(f"URL: {info['url']}\n")


if __name__ == '__main__':
    main()
