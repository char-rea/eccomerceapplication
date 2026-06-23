from django.shortcuts import render
from .functions.reddit import get_reddit_posts


def reddit_feed(request):
    # Call our helper function to fetch posts
    """
    View to render the Reddit feed.

    This view fetches the posts from the `get_reddit_posts` helper
    function and passes them into the `reddit_feed.html` template.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        An HTTP response containing the rendered template.
    """
    posts = get_reddit_posts("python")

    # Pass the posts into the template
    return render(request, "reddit_feed.html", {"posts": posts})
