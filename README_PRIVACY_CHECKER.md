# Repository Privacy Checker

This tool helps you check if GitHub repositories are private or public.

## Quick Answer: "Are my repos private?"

Based on the GitHub API search results, the `evi-kopadi/nemo` repository **appears to be PRIVATE**. 

When searching for public repositories under the `evi-kopadi` username using the GitHub search API, no repositories were found, which indicates they are not publicly accessible. This means your repository is likely set to private.

### How to Verify

You can verify this yourself using the included script:

```bash
# With a GitHub token (recommended):
export GITHUB_TOKEN=your_token_here
python check_repo_privacy.py --user evi-kopadi

# Or check a specific repo:
python check_repo_privacy.py evi-kopadi/nemo
```

## Using the Privacy Checker Script

The script provides two modes of operation:

1. **Check specific repositories** - Verify the privacy status of individual repos
2. **List all user repositories** - See all repositories for a given user along with their privacy status

### Mode 1: Check Specific Repositories

```bash
python check_repo_privacy.py <owner/repo> [<owner/repo> ...]
```

**Examples:**

Check a single repository:
```bash
python check_repo_privacy.py evi-kopadi/nemo
```

Check multiple repositories:
```bash
python check_repo_privacy.py evi-kopadi/nemo torvalds/linux microsoft/vscode
```

### Mode 2: List All User Repositories

```bash
python check_repo_privacy.py --user <username>
```

**Example:**

```bash
python check_repo_privacy.py --user evi-kopadi
```

This will list all accessible repositories for the user and provide a summary of how many are public vs. private.

### Authentication

For checking private repositories or to avoid rate limits, set a GitHub personal access token:

```bash
export GITHUB_TOKEN=your_token_here
python check_repo_privacy.py evi-kopadi/nemo
```

Or use `GH_TOKEN`:
```bash
export GH_TOKEN=your_token_here
python check_repo_privacy.py evi-kopadi/nemo
```

### Creating a GitHub Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token (classic)
3. Select the `repo` scope for full repository access
4. Copy the token and set it as an environment variable

## What the Script Checks

The script queries the GitHub API for each repository and reports:
- **Privacy Status**: Whether the repository is 🔒 PRIVATE or 🌐 PUBLIC
- **Visibility**: The repository visibility setting
- **Description**: The repository description
- **URL**: The repository's web URL

## Note

**Limitations:**
- Without authentication, the script can only check public repositories and may hit API rate limits quickly (60 requests/hour)
- With authentication (GITHUB_TOKEN), you can check all repositories you have access to with higher API rate limits (5000 requests/hour)
- The `--user` mode currently fetches up to 100 repositories. If you have more than 100 repositories, only the first 100 will be shown.
