"""
github_service.py - GitHub API Integration Service

Handles authenticating and communicating with the GitHub REST API to fetch
repositories tree files, read raw codebase scripts, and retrieve commits diff lists.
"""

from typing import List, Dict, Any


import requests
from typing import List, Dict, Any
from backend.app.config import get_settings

class GitHubService:
    """
    Client wrapper for querying GitHub repositories files, commits, and diffs.
    """
    def __init__(self, token: str = None) -> None:
        self.base_url = "https://api.github.com"
        self.settings = get_settings()
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        github_token = token or self.settings.GITHUB_TOKEN
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    def _parse_repo_name(self, repo_url: str) -> str:
        """Helper to extract 'owner/repo' from GitHub URL if URL is passed."""
        if not repo_url:
            return ""
        if "github.com/" in repo_url:
            # e.g., https://github.com/octocat/Hello-World
            parts = repo_url.split("github.com/")[-1].split("/")
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1]}"
        return repo_url

    def fetch_repo_files_list(self, repo: str) -> List[str]:
        """
        Retrieves file paths of all modules in a repository workspace.
        """
        repo_name = self._parse_repo_name(repo)
        if not repo_name:
            return []
        
        # Try main first, fallback to master
        url = f"{self.base_url}/repos/{repo_name}/git/trees/main?recursive=1"
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            if res.status_code == 404:
                url = f"{self.base_url}/repos/{repo_name}/git/trees/master?recursive=1"
                res = requests.get(url, headers=self.headers, timeout=10)
            res.raise_for_status()
            data = res.json()
            return [node["path"] for node in data.get("tree", []) if node.get("type") == "blob"]
        except Exception as e:
            print(f"? GitHubService fetch_repo_files_list error: {e}")
            return []

    def fetch_file_contents(self, repo: str, file_path: str, ref: str = "main") -> str:
        """
        Retrieves raw code file contents from a specific repo branch/commit.
        """
        repo_name = self._parse_repo_name(repo)
        if not repo_name:
            return ""
            
        url = f"{self.base_url}/repos/{repo_name}/contents/{file_path}"
        headers = dict(self.headers)
        headers["Accept"] = "application/vnd.github.v3.raw"
        
        try:
            res = requests.get(url, headers=headers, params={"ref": ref}, timeout=10)
            if res.status_code == 404 and ref == "main":
                res = requests.get(url, headers=headers, params={"ref": "master"}, timeout=10)
            res.raise_for_status()
            return res.text
        except Exception as e:
            print(f"? GitHubService fetch_file_contents error: {e}")
            return ""

    def fetch_recent_commits(self, repo: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves commit logs summary.
        """
        repo_name = self._parse_repo_name(repo)
        if not repo_name:
            return []
            
        url = f"{self.base_url}/repos/{repo_name}/commits"
        try:
            res = requests.get(url, headers=self.headers, params={"per_page": limit}, timeout=10)
            res.raise_for_status()
            data = res.json()
            commits = []
            for item in data:
                commits.append({
                    "sha": item.get("sha", ""),
                    "author": item.get("commit", {}).get("author", {}).get("name", ""),
                    "message": item.get("commit", {}).get("message", ""),
                    "date": item.get("commit", {}).get("author", {}).get("date", "")
                })
            return commits
        except Exception as e:
            print(f"? GitHubService fetch_recent_commits error: {e}")
            return []

    def fetch_commit_diff(self, repo: str, commit_hash: str) -> str:
        """
        Retrieves code changes diff patch for a single commit.
        """
        repo_name = self._parse_repo_name(repo)
        if not repo_name or not commit_hash:
            return ""
            
        url = f"{self.base_url}/repos/{repo_name}/commits/{commit_hash}"
        headers = dict(self.headers)
        headers["Accept"] = "application/vnd.github.diff"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            return res.text
        except Exception as e:
            print(f"? GitHubService fetch_commit_diff error: {e}")
            return ""

