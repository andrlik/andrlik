# build_readme.py
#
# Copyright (c) 2025 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "feedparser",
#     "python-graphql-client",
# ]
# ///
from datetime import datetime
import os

import feedparser
from python_graphql_client import GraphqlClient

client = GraphqlClient(endpoint="https://api.github.com/graphql")

TOKEN = os.environ.get("ANDRLIK_TOKEN", "")

MAX_ITEMS = 6


def make_query(after_cursor: str | None = None) -> str:
    """
    Generate the query to feed to Github GraphQL API.
    With thanks and apologies to Simon Willison.
    """
    return """
query {
  search(first: 100, type:REPOSITORY, query:"is:public owner:andrlik sort:updated", after: AFTER) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      __typename
      ... on Repository {
        name
        description
        url
        releases(orderBy: {field: CREATED_AT, direction: DESC}, first: 1) {
          totalCount
          nodes {
            name
            publishedAt
            url
          }
        }
      }
    }
  }
}
""".replace("AFTER", f"{after_cursor}" if after_cursor else "null")


def get_recent_releases_as_md_list(oauth_token: str, max_items: int) -> str:
    """Use Github GraphQL to fetch recent releases from my repositories."""
    repos = []
    releases = []
    repo_names = set()
    has_next_page = True
    after_cursor = None

    while has_next_page:
        data = client.execute(
            query=make_query(after_cursor),
            headers={"Authorization": f"Bearer {oauth_token}"},
        )
        for repo in data["data"]["search"]["nodes"]:
            if repo["releases"]["totalCount"] > 0 and repo["name"] not in repo_names:
                repos.append(repo)
                repo_names.add(repo["name"])
                releases.append(
                    {
                        "repo": repo["name"],
                        "repo_url": repo["url"],
                        "release": repo["releases"]["nodes"][0]["name"]
                        .replace(repo["name"], "")
                        .strip(),
                        "published_at": repo["releases"]["nodes"][0][
                            "publishedAt"
                        ].split("T")[0],
                        "url": repo["releases"]["nodes"][0]["url"],
                    }
                )
        after_cursor = data["data"]["search"]["pageInfo"]["endCursor"]
        has_next_page = data["data"]["search"]["pageInfo"]["hasNextPage"]
    releases.sort(key=lambda r: r["published_at"], reverse=True)
    release_md_list = "\n".join(
        [
            f"* [{r['repo']} {r['release']}]({r['url']}) - {r['published_at']}"
            for r in releases[:max_items]
        ]
    )
    return release_md_list


def get_blog_entries_as_md_list(max_items: int) -> str:
    """Get the most recent entries and return as a markdown list."""
    blog = feedparser.parse("https://www.andrlik.org/index.xml")
    recent_entries = blog.entries[:max_items]
    entry_md_list = "\n".join(
        [
            f"* [{e.title}]({e.link}) - {datetime.strptime(e.published, '%a, %d %b %Y %H:%M:%S %z').strftime('%Y-%m-%d')}"
            for e in recent_entries
        ]
    )
    return entry_md_list


if __name__ == "__main__":
    entries_list = get_blog_entries_as_md_list(max_items=MAX_ITEMS)
    releases_list = get_recent_releases_as_md_list(
        oauth_token=TOKEN, max_items=MAX_ITEMS
    )
    content_str = f"""

### Recent releases

{releases_list}

### Recent blog posts

{entries_list}

More on [www.andrlik.org](https://www.andrlik.org)

    """
    print(content_str)
