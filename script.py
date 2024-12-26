import os
import datetime
import time
import git
import schedule
import shutil
from pathlib import Path

class GitAutoCommitter:
    def __init__(self, repo_path, github_url):
        self.repo_path = Path(repo_path)
        self.github_url = github_url
        self.repo = None

    def setup_repo(self):
        """Initialize repository if it doesn't exist"""
        try:
            if self.repo_path.exists():
                # If directory exists but is not a git repo, remove it
                if not (self.repo_path / '.git').exists():
                    shutil.rmtree(self.repo_path)
                    self.repo_path.mkdir(parents=True, exist_ok=True)
                    self.repo = git.Repo.clone_from(self.github_url, self.repo_path)
                else:
                    # If it's already a git repo, just use it
                    self.repo = git.Repo(self.repo_path)
                    # Make sure we have the right remote
                    if 'origin' not in [remote.name for remote in self.repo.remotes]:
                        self.repo.create_remote('origin', self.github_url)
                    # Pull latest changes
                    origin = self.repo.remote('origin')
                    origin.pull()
            else:
                # Fresh clone if directory doesn't exist
                self.repo_path.mkdir(parents=True, exist_ok=True)
                self.repo = git.Repo.clone_from(self.github_url, self.repo_path)
            
            print(f"Repository setup complete at {self.repo_path}")
            
        except git.exc.GitCommandError as e:
            print(f"Git error: {e}")
            raise
        except Exception as e:
            print(f"Error setting up repository: {e}")
            raise

    def update_readme(self):
        """Update README.md with timestamp"""
        readme_path = self.repo_path / 'README.md'
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(readme_path, 'a') as f:
            f.write(f'\nAuto-commit at: {timestamp}\n')

    def make_commit(self):
        """Make a commit with the current changes"""
        try:
            # Pull latest changes first
            origin = self.repo.remote('origin')
            origin.pull()

            # Update readme and make commit
            self.update_readme()
            self.repo.git.add(".")

            commit_message = f"Auto commit at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.repo.index.commit(commit_message)

            # Push changes
            origin.push()

            print(f"Successfully made commit at {datetime.datetime.now()}")
        except Exception as e:
            print(f"Error making commit: {str(e)}")

def main():
    # Get the current user's home directory
    home_dir = str(Path.home())
    
    # Create a directory for the repository in the home directory
    REPO_PATH = os.path.join(home_dir, "github_automate", "auto_schedular")
    GITHUB_URL = "https://github.com/SAHIL-Sharma21/auto_schedular.git"

    committer = GitAutoCommitter(REPO_PATH, GITHUB_URL)
    committer.setup_repo()

    # Schedule daily commit at 10 PM
    schedule.every().day.at("22:00").do(committer.make_commit)

    print("Auto-commit scheduler started...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()