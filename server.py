
from mcp.server import MCPServer
import httpx


mcp = MCPServer("DevPilotMCP")


@mcp.tool()
def get_server_status() -> dict[str, str]:
    """Return the current status of the DevPilot MCP server."""
    return {
        "server": "DevPilotMCP",
        "status": "ok",
        "mode": "development",
    }


@mcp.tool()
def get_github_repository(owner: str, repo: str) -> dict:
    """Get public GitHub repository details using its owner and repository name."""
    if not owner.strip() or not repo.strip():
        return {"error": "Owner and repository name are required."}

    url = f"https://api.github.com/repos/{owner.strip()}/{repo.strip()}"

    try:
        response = httpx.get(
            url,
            headers={"Accept": "application/vnd.github+json"},
            timeout=10.0,
            follow_redirects=False,
        )

        if response.status_code == 404:
            return {"error": "Repository not found or not publicly accessible."}

        if response.status_code == 403:
            return {"error": "GitHub API rate limit or access restriction reached."}

        response.raise_for_status()
        data = response.json()

        return {
            "name": data["full_name"],
            "description": data.get("description"),
            "url": data["html_url"],
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "language": data.get("language"),
            "open_issues": data["open_issues_count"],
            "default_branch": data["default_branch"],
        }

    except httpx.TimeoutException:
        return {"error": "GitHub API request timed out."}
    except httpx.HTTPStatusError:
        return {"error": "GitHub API returned an unsuccessful response."}
    except httpx.RequestError:
        return {"error": "Could not connect to the GitHub API."}


if __name__ == "__main__":
    mcp.run(transport="stdio")
