import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


API_ROOT = "https://www.googleapis.com/blogger/v3"


def api_request(url, token, method="GET", payload=None):
    headers = {
        "Authorization": "Bearer " + token,
        "Accept": "application/json",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else {}


def main():
    print("Blogger Auto Publisher")
    blog_id = os.getenv("BLOGGER_BLOG_ID", "").strip()
    access_token = os.getenv("BLOGGER_ACCESS_TOKEN", "").strip()

    if not blog_id:
        raise SystemExit("ERROR: BLOGGER_BLOG_ID is not configured.")
    if not access_token:
        raise SystemExit("ERROR: BLOGGER_ACCESS_TOKEN is not configured.")

    try:
        blog = api_request(f"{API_ROOT}/blogs/{urllib.parse.quote(blog_id, safe='')}", access_token)
        print("Connection successful!")
        print("Blog title:", blog.get("name", "Unknown"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Blogger API error during connection check: HTTP {error.code}\n{details}")
    except Exception as error:
        raise SystemExit(f"Connection failed: {error}")

    article_path = Path("article.json")
    if not article_path.exists():
        print("No article.json found. Connection check only; nothing was published.")
        return

    try:
        article = json.loads(article_path.read_text(encoding="utf-8"))
    except Exception as error:
        raise SystemExit(f"ERROR: article.json is not valid JSON: {error}")

    title = str(article.get("title", "")).strip()
    content = str(article.get("content", "")).strip()
    labels = article.get("labels", [])

    if not title or not content:
        raise SystemExit("ERROR: article.json must contain non-empty 'title' and 'content'.")
    if title == "عنوان المقال هنا" or "ضع محتوى المقال" in content:
        raise SystemExit("ERROR: article.json is still the template. Replace it with a reviewed article before publishing.")
    if not isinstance(labels, list) or not all(isinstance(label, str) for label in labels):
        raise SystemExit("ERROR: 'labels' must be a list of strings.")

    approved = os.getenv("PUBLISH_APPROVED", "false").strip().lower() == "true"
    if not approved:
        print("ARTICLE READY FOR REVIEW — approval is false.")
        print("Title:", title)
        print("Labels:", ", ".join(labels))
        print("Nothing was published. Review article.json before approving a run.")
        return

    post_payload = {"title": title, "content": content}
    if labels:
        post_payload["labels"] = labels

    url = f"{API_ROOT}/blogs/{urllib.parse.quote(blog_id, safe='')}/posts/"
    try:
        result = api_request(url, access_token, method="POST", payload=post_payload)
        print("PUBLISH SUCCESS")
        print("Post title:", result.get("title", title))
        print("Post URL:", result.get("url", "(URL not returned)"))
        print("Post ID:", result.get("id", "(ID not returned)"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise SystemExit(
            f"Blogger publish error: HTTP {error.code}\n{details}\n"
            "If this is a scope error, configure Google OAuth with Blogger write access "
            "(https://www.googleapis.com/auth/blogger), then refresh the access token."
        )


if __name__ == "__main__":
    main()
