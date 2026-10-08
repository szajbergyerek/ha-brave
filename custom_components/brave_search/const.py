DOMAIN = "brave_search"

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

API_NAME = "Brave Search"
API_PROMPT = (
    "You can use the brave_search tool to search the public internet for "
    "current information that you do not already know."
)

SERVICE_SEARCH = "search"

TOOL_NAME = "brave_search"
TOOL_DESCRIPTION = (
    "Search the public internet for current information using the Brave Search "
    "engine. Use this when you need up-to-date facts, news, or any information "
    "that is not part of your training data or the Home Assistant state."
)

CONF_RESULT_COUNT = "count"
DEFAULT_RESULT_COUNT = 5
MIN_RESULT_COUNT = 1
MAX_RESULT_COUNT = 10

REQUEST_TIMEOUT_SECONDS = 10
