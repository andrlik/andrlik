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
# ]
# ///
from datetime import datetime

import feedparser

MAX_ITEMS = 6

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
    content_str = f"""

### Recent blog posts

{entries_list}

More on [www.andrlik.org](https://www.andrlik.org)

    """
    print(content_str)
