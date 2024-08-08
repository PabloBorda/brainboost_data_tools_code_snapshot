import requests
import subprocess
import os

class GitHubBatchCloner:

    def __init__(self) -> None:
        pass

    def get_list_of_repositories_for_usernames(self, usernames):
        all_repos = []
        for username in usernames:
            repos = []
            page = 1
            while True:
                url = f"https://api.github.com/users/{username}/repos?page={page}&per_page=100"
                response = requests.get(url)
                if response.status_code != 200:
                    print(f"Failed to fetch repositories for user {username}. HTTP Status code: {response.status_code}")
                    break
                page_repos = response.json()
                if not page_repos:
                    break
                repos.extend(page_repos)
                page += 1
            all_repos.extend(repos)
        return all_repos

    def get_github_repos(self, usernames):
        repos = self.get_list_of_repositories_for_usernames(usernames)
        clone_urls = [repo['clone_url'] for repo in repos]
        return len(clone_urls), clone_urls

    def clone_or_update_repo(self, repo_url, dest_dir):
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        repo_path = os.path.join(dest_dir, repo_name)
        if not os.path.exists(repo_path):
            print(f"Cloning {repo_url} into {repo_path}...")
            subprocess.run(['git', 'clone', repo_url, repo_path])
        else:
            print(f"Repository {repo_name} already exists. Pulling updates in {repo_path}...")
            subprocess.run(['git', '-C', repo_path, 'fetch'])
            subprocess.run(['git', '-C', repo_path, 'pull'])

    def clone_repos(self, clone_urls, dest_dir):
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        for url in clone_urls:
            self.clone_or_update_repo(url, dest_dir)

