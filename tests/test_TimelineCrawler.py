from zilean import TimelineCrawler


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