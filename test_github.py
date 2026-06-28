"""
Test GitHub Service Integration
"""
from backend.services.github_service import GitHubService
from backend.app.config import get_settings

print("🔍 Testing GitHub Integration...\n")

# Get settings
settings = get_settings()
print(f"✅ GitHub Token loaded: {settings.GITHUB_TOKEN[:10]}...")

# Initialize service
service = GitHubService(settings.GITHUB_TOKEN)

# Test with a public repo
repo_url = "https://github.com/octocat/Hello-World"
print(f"\n📦 Testing with repo: {repo_url}")

# Test 1: Fetch recent commits
print("\n📋 Test 1: Fetching recent commits...")
try:
    commits = service.fetch_recent_commits(repo_url, limit=3)
    print(f"✅ Fetched {len(commits)} commits:")
    for commit in commits:
        sha = commit.get('sha', 'N/A')[:7]
        message = commit.get('commit', {}).get('message', 'N/A')
        print(f"   - {sha}: {message[:60]}")
except Exception as e:
    print(f"❌ Error fetching commits: {e}")

# Test 2: Fetch repo files
print("\n📁 Test 2: Fetching repository files...")
try:
    files = service.fetch_repo_files_list(repo_url)
    print(f"✅ Found {len(files)} files/folders")
    # Show first 5 files
    for f in files[:5]:
        print(f"   - {f}")
except Exception as e:
    print(f"❌ Error fetching files: {e}")

# Test 3: Fetch file content
print("\n📄 Test 3: Fetching file content...")
try:
    content = service.fetch_file_contents(repo_url, "README.md", "master")
    print(f"✅ README.md size: {len(content)} bytes")
    # Show first 100 chars
    print(f"   Preview: {content[:100]}...")
except Exception as e:
    print(f"❌ Error fetching file: {e}")

print("\n✅ GitHub service tests complete!")