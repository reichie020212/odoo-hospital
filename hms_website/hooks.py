def post_init_hook(env):
    """Set /hospital as the default website homepage on install."""
    website = env["website"].search([], limit=1)
    if website and not website.homepage_url:
        website.homepage_url = "/hospital"
