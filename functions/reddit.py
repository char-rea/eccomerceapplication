import requests

def get_reddit_posts(subreddit="python"):
    """
    API for Reddit Posts to read
    """
    # Build the URL for the subreddit's JSON feed
    url = f"https://www.reddit.com/r/{subreddit}/.json"
    headers = {
        "User-Agent": "DjangoEcommerceApp/1.0"
    } 

    # Make the request
    response = requests.get(url, headers=headers)

    # Handle errors
    if response.status_code != 200:
        print("Failed to fetch data.")
        return None

    # Parse the JSON response
    data = response.json()
    posts = []
    print(data)
    
    # Extract useful fields from each post
    for item in data["data"]["children"]:
        post = item["data"]
        posts.append({
            "title": post["title"],
            "author": post["author"],
            "url": post["url"]
        })

    return posts