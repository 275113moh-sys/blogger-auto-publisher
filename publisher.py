import os
import json
import urllib.request
import urllib.error


def main():
    print("Blogger Auto Publisher")
    print("Checking required configuration...")

    blog_id = os.getenv("BLOGGER_BLOG_ID")
    access_token = os.getenv("BLOGGER_ACCESS_TOKEN")

    if not blog_id:
        print("ERROR: BLOGGER_BLOG_ID is not configured.")
        return

    if not access_token:
        print("ERROR: BLOGGER_ACCESS_TOKEN is not configured.")
        return

    url = (
        "https://www.googleapis.com/blogger/v3/blogs/"
        + blog_id
    )

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": "Bearer " + access_token,
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))

        print("Connection successful!")
        print("Blog title:", data.get("name", "Unknown"))
        print("The script has not published any posts.")

    except urllib.error.HTTPError as error:
        print("Blogger API error:", error.code)
        print(error.read().decode("utf-8", errors="replace"))

    except Exception as error:
        print("Connection failed:", str(error))


if __name__ == "__main__":
    main()
