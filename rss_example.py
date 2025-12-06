import feedparser

FEED_URL = "https://www.marinelink.com/news/rss"


def main() -> None:
    """
    Simple demo that fetches the RSS feed and prints the first 10 items.
    This is a starting point for the future news-writing bot.
    """
    feed = feedparser.parse(FEED_URL)

    # Basic feed metadata
    print("Feed title:", getattr(feed.feed, "title", ""))
    print("Feed link :", getattr(feed.feed, "link", ""))
    print()

    # First 10 items
    for item in feed.entries[:10]:
        print("Title     :", getattr(item, "title", ""))
        print("Link      :", getattr(item, "link", ""))
        print("Published :", getattr(item, "published", ""))
        summary = getattr(item, "summary", "")
        print("Summary   :", summary[:200], "..." if len(summary) > 200 else "")
        print("-" * 60)


if __name__ == "__main__":
    main()



