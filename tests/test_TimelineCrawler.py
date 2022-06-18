from zilean import TimelineCrawler, DummyWatcher

import os

# Current file location:
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

crawl_result_file = os.path.join(__location__, "crawl_result.json")

def test_invalid_api_type():
    """Test invalid type for `api_key` keyword argument."""
    try:
        TimelineCrawler(api_key=12345, region="kr", 
                        tier="CHALLENGER", queue="RANKED_SOLO_5x5")
    except TypeError:
        pass;


def test_invalid_region_type():
    """Test invalid type for `region` keyword argument."""
    try:
        TimelineCrawler(api_key="key", region=1235, 
                        tier="IRON", queue="RANKED_SOLO_5x5")
    except TypeError:
        pass;


def test_invalid_tier_type():
    """Test invalid type for `tier` keyword argument."""
    try:
        TimelineCrawler(api_key="key", region="kr", 
                        tier=123435, queue="RANKED_SOLO_5x5")
    except TypeError:
        pass;


def test_invalid_queue_type():
    """Test invalid type for `queue` keyword argument."""
    try:
        TimelineCrawler(api_key="key", region="kr", 
                        tier="IRON", queue=12345)
    except TypeError:
        pass;


def test_invalid_region_value():
    """Test invalid value for `region` keyword argument."""
    try:
        TimelineCrawler(api_key="key", region="KR", 
                        tier="IRON", queue="RANKED_SOLO_5x5")
    except ValueError:
        pass;


def test_invalid_tier_value():
    """Test invalid value for `tier` keyword argument."""
    try:
        TimelineCrawler(api_key="key", region="na1", 
                        tier="iron", queue="RANKED_SOLO_5x5")
    except ValueError:
        pass;


def test_invalid_queue_value():
    """Test invalid value for `queue` keyword argument."""
    try:
        TimelineCrawler(api_key="key", region="ru", 
                        tier="GOLD", queue="RANKED_SOLO_5X5")
    except ValueError:
        pass;


def test_crawl_to_disk():
    """Generic test for crawl with saved result on disk."""
    crawler = TimelineCrawler(api_key="key", region="na1", 
                              tier="GOLD", queue="RANKED_SOLO_5x5",
                              dummy_watcher=DummyWatcher())
    crawler.crawl(1, file=crawl_result_file)
    # Should be saved to disk
    assert os.path.exists(crawl_result_file)
    # Crawling again with the same file should bring error
    try:
        crawler.crawl(2, file=crawl_result_file)
    except ValueError:
        pass
    # Clean up
    os.remove(crawl_result_file)


def test_crawl_no_to_disk():
    """Generic test for crawl and don't save result on disk."""
    crawler = TimelineCrawler(api_key="key", region="na1", 
                              tier="GOLD", queue="RANKED_SOLO_5x5",
                              dummy_watcher=DummyWatcher())
    crawler.crawl(1)
    # Should not be saved to disk
    assert not os.path.exists(crawl_result_file)


def test_crawl_matchId():
    """
    Test the matchId for the crawled dummy results with
    different tier options. There should be two matches
    maximum, and the matchids are "TIER_1" and "TIER_2".
    """
    # For GOLD
    crawler = TimelineCrawler(api_key="key", region="na1", 
                              tier="GOLD", queue="RANKED_SOLO_5x5",
                              dummy_watcher=DummyWatcher())
    result = crawler.crawl(4, cutoff=0)
    # There should be only 2 matches
    assert type(result) == list
    assert len(result) == 2
    # The matchIds should be dummy_1 and dummy_2
    assert result[0]['metadata']['matchId'] == "GOLD_1"
    assert result[1]['metadata']['matchId'] == "GOLD_2"

    # For CHALLENGER
    crawler = TimelineCrawler(api_key="key", region="na1", 
                              tier="CHALLENGER", queue="RANKED_SOLO_5x5",
                              dummy_watcher=DummyWatcher())
    result = crawler.crawl(1, cutoff=0)
    # There should be only 1 matches
    assert type(result) == list
    assert len(result) == 1
    # The matchIds should be dummy_1 and dummy_2
    assert result[0]['metadata']['matchId'] == "CHALLENGER_1"

    # For GRANDMASTER
    crawler = TimelineCrawler(api_key="key", region="na1", 
                              tier="GRANDMASTER", queue="RANKED_SOLO_5x5",
                              dummy_watcher=DummyWatcher())
    result = crawler.crawl(1, cutoff=0)
    assert result[0]['metadata']['matchId'] == "GRANDMASTER_1"

    # For MASTER
    crawler = TimelineCrawler(api_key="key", region="na1", 
                              tier="MASTER", queue="RANKED_SOLO_5x5",
                              dummy_watcher=DummyWatcher())
    result = crawler.crawl(1, cutoff=0)
    assert result[0]['metadata']['matchId'] == "MASTER_1"