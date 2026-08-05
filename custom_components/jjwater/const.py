"""Constants for the Jinjiang Water integration."""
from typing import Final

DOMAIN: Final = "jjwater"

# Config keys
CONF_USER_KH: Final = "user_kh"
CONF_TOKEN: Final = "token"

# Defaults
DEFAULT_NAME: Final = "晋江水务"
DEFAULT_SCAN_INTERVAL_HOURS: Final = 2

# API Base URL
BASE_URL: Final = "https://wwt.jinjiangwater.com/jjapis"
DEFAULT_UPDATE_INTERVAL = 18000  # 默认刷新频率：5小时
