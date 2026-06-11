# Production configuration for the Superset VM deployment.
# Loaded automatically because PYTHONPATH=/app/pythonpath in the lean image.
# Overrides any defaults defined in superset/config.py.

import logging
import os
from urllib.parse import quote_plus

from celery.schedules import crontab
from flask_caching.backends.filesystemcache import FileSystemCache

logger = logging.getLogger(__name__)

PREVIOUS_SECRET_KEY = os.getenv("PREVIOUS_SECRET_KEY")


def _csv_env(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# ---------------------------------------------------------------------------
# Metadata database (external PostgreSQL) — values come from env vars
# ---------------------------------------------------------------------------
DATABASE_DIALECT = os.getenv("DATABASE_DIALECT", "postgresql")
DATABASE_USER = os.environ["DATABASE_USER"]
DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]
DATABASE_HOST = os.environ["DATABASE_HOST"]
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_DB = os.environ["DATABASE_DB"]

# URL-encode user/password — necessário quando contém '@', ':', '/', etc.
_db_user = quote_plus(DATABASE_USER)
_db_pass = quote_plus(DATABASE_PASSWORD)

_ssl_mode = os.getenv("DATABASE_SSL_MODE", "")
_ssl_suffix = f"?sslmode={_ssl_mode}" if _ssl_mode else ""

SQLALCHEMY_DATABASE_URI = (
    f"{DATABASE_DIALECT}://"
    f"{_db_user}:{_db_pass}@"
    f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}{_ssl_suffix}"
)

# ---------------------------------------------------------------------------
# Redis cache / Celery broker
# ---------------------------------------------------------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "192.168.15.74")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", "1")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
_redis_auth = f":{quote_plus(REDIS_PASSWORD)}@" if REDIS_PASSWORD else ""

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
    "CACHE_REDIS_PASSWORD": REDIS_PASSWORD or None,
}
DATA_CACHE_CONFIG = CACHE_CONFIG
THUMBNAIL_CACHE_CONFIG = CACHE_CONFIG


class CeleryConfig:
    broker_url = f"redis://{_redis_auth}{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = (
        "superset.sql_lab",
        "superset.tasks.scheduler",
        "superset.tasks.thumbnails",
        "superset.tasks.cache",
    )
    result_backend = f"redis://{_redis_auth}{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    worker_prefetch_multiplier = 1
    task_acks_late = False
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

# ---------------------------------------------------------------------------
# Idioma — pt_BR padrão, com inglês disponível
# ---------------------------------------------------------------------------
BABEL_DEFAULT_LOCALE = "pt_BR"
LANGUAGES = {
    "pt_BR": {"flag": "br", "name": "Português (Brasil)"},
    "en": {"flag": "us", "name": "English"},
}

# ---------------------------------------------------------------------------
# Formatos numéricos / moeda (pt-BR)
# ---------------------------------------------------------------------------
D3_FORMAT = {
    "decimal": ",",
    "thousands": ".",
    "grouping": [3],
    "currency": ["R$ ", ""],
}

# Formatos de data / hora (pt-BR, 24h)
D3_TIME_FORMAT = {
    "dateTime": "%d/%m/%Y, %H:%M:%S",
    "date": "%d/%m/%Y",
    "time": "%H:%M:%S",
    "periods": ["AM", "PM"],
    "days": [
        "Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira",
        "Quinta-feira", "Sexta-feira", "Sábado",
    ],
    "shortDays": ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"],
    "months": [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
    ],
    "shortMonths": [
        "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
        "Jul", "Ago", "Set", "Out", "Nov", "Dez",
    ],
}

CURRENCIES = ["BRL", "USD", "EUR"]

# ---------------------------------------------------------------------------
# Branding
# ---------------------------------------------------------------------------
APP_NAME = os.getenv("SUPERSET_APP_NAME", "linhalis")
APP_ICON = os.getenv(
    "SUPERSET_APP_ICON",
    "/static/assets/images/superset-logo-horiz.png",
)
LOGO_TOOLTIP = os.getenv("SUPERSET_LOGO_TOOLTIP", APP_NAME)
LOGO_TARGET_PATH = "/superset/welcome/"
FAVICONS = [{"href": "/static/assets/images/favicon.png"}]

# ---------------------------------------------------------------------------
# Tema — paleta Linhalis
# ---------------------------------------------------------------------------
_LINHALIS_NAVY = "#102A43"
_LINHALIS_NAVY_DEEP = "#061827"
_LINHALIS_BLUE = "#13577A"
_LINHALIS_CYAN = "#159CC5"
_LINHALIS_CYAN_HOVER = "#2BBCE2"
_LINHALIS_CYAN_ACTIVE = "#0F7EA3"
_LINHALIS_ICE = "#DDF7FF"
_LINHALIS_SKY = "#AEEBFA"

THEME_DEFAULT = {
    "token": {
        "brandAppName": APP_NAME,
        "brandLogoAlt": APP_NAME,
        "brandLogoUrl": APP_ICON,
        "brandLogoMargin": "18px 0",
        "brandLogoHref": "/",
        "brandLogoHeight": "24px",
        "brandSpinnerUrl": None,
        "brandSpinnerSvg": None,
        "colorPrimary": _LINHALIS_CYAN,
        "colorPrimaryHover": _LINHALIS_CYAN_HOVER,
        "colorPrimaryActive": _LINHALIS_CYAN_ACTIVE,
        "colorLink": _LINHALIS_CYAN,
        "colorLinkHover": _LINHALIS_CYAN_HOVER,
        "colorError": "#dc2626",
        "colorWarning": "#f59e0b",
        "colorSuccess": "#10b981",
        "colorInfo": _LINHALIS_BLUE,
        "colorTextBase": _LINHALIS_NAVY,
        "colorBgBase": "#f7fcff",
        "colorBgLayout": "#eef8fc",
        "colorBgContainer": "#ffffff",
        "colorBgElevated": "#ffffff",
        "colorBgSpotlight": _LINHALIS_NAVY,
        "colorBorder": "#ccebf4",
        "colorBorderSecondary": "#e2f4fa",
        "fontUrls": [],
        "fontFamily": "Aptos, 'Segoe UI', Helvetica, Arial, sans-serif",
        "fontFamilyCode": "'IBM Plex Mono', 'Courier New', monospace",
        "transitionTiming": 0.3,
        "brandIconMaxWidth": 37,
        "fontSizeXS": "8",
        "fontSizeXXL": "28",
        "fontWeightNormal": "400",
        "fontWeightLight": "300",
        "fontWeightStrong": "500",
        "fontWeightBold": "700",
        "colorEditorSelection": "#fff5cf",
    },
    "algorithm": "default",
}

THEME_DARK = {
    **THEME_DEFAULT,
    "token": {
        **THEME_DEFAULT["token"],
        "colorPrimary": _LINHALIS_CYAN,
        "colorPrimaryHover": _LINHALIS_CYAN_HOVER,
        "colorPrimaryActive": _LINHALIS_CYAN_ACTIVE,
        "colorLink": _LINHALIS_SKY,
        "colorLinkHover": _LINHALIS_ICE,
        "colorError": "#fb7185",
        "colorWarning": "#fbbf24",
        "colorSuccess": "#34d399",
        "colorInfo": _LINHALIS_SKY,
        "colorBgBase": _LINHALIS_NAVY_DEEP,
        "colorBgLayout": "#0b2137",
        "colorBgContainer": _LINHALIS_NAVY,
        "colorBgElevated": "#123756",
        "colorBgSpotlight": "#174767",
        "colorBorder": "#1d5874",
        "colorBorderSecondary": "#173f59",
        "colorTextBase": "#ecfbff",
        "colorEditorSelection": "#0f5f7b",
    },
    "algorithm": "dark",
}

# ---------------------------------------------------------------------------
# Paletas de cores para charts
# ---------------------------------------------------------------------------
# Categórica (padrão para séries em barras, linhas, pizza, etc.).
EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "linhalis",
        "label": "linhalis",
        "description": "Paleta Linhalis para gráficos categóricos",
        "isDefault": True,
        "colors": [
            "#102A43",
            "#13577A",
            "#159CC5",
            "#AEEBFA",
            "#DDF7FF",
            "#0B3A57",
            "#1E7898",
            "#42C7E8",
            "#6FDDF4",
            "#7EA6B8",
            "#174767",
            "#ECFBFF",
        ],
    },
]

# Sequencial (gradiente para heatmaps, choropleth, escalas de intensidade)
EXTRA_SEQUENTIAL_COLOR_SCHEMES = [
    {
        "id": "linhalisLinear",
        "label": "linhalis linear",
        "description": "Gradiente linear Linhalis para heatmaps e escalas de intensidade",
        "isDiverging": False,
        "isDefault": True,
        "colors": [
            "#ECFBFF",
            "#DDF7FF",
            "#C6F0FC",
            "#AEEBFA",
            "#6FDDF4",
            "#42C7E8",
            "#159CC5",
            "#13577A",
            "#102A43",
            "#061827",
        ],
    },
]

# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------
FEATURE_FLAGS = {
    # Embarcar dashboards em outros sistemas via SDK/iframe
    "EMBEDDED_SUPERSET": True,
    # Alertas e Relatórios agendados (requer Celery worker + beat para realmente disparar)
    "ALERT_REPORTS": True,
    # Aplica Row Level Security também em queries do SQL Lab
    "RLS_IN_SQLLAB": True,
    # Controle de acesso por dashboard via roles (necessário para RLS por dashboard)
    "DASHBOARD_RBAC": True,
    # Habilita templating Jinja em datasets e queries (templates / macros / current_user)
    "ENABLE_TEMPLATE_PROCESSING": True,
    # Permite subqueries ad-hoc no Explore (query builder avançado)
    "ALLOW_ADHOC_SUBQUERY": True,
    # Drill-by / Drill-to-detail (drill em charts e dashboards)
    "DRILL_BY": True,
    "DRILL_TO_DETAIL": True,
    # Tags em dashboards e charts
    "TAGGING_SYSTEM": True,
    # Templates CSS reutilizáveis para dashboards
    "CSS_TEMPLATES": True,
}
GUEST_TOKEN_JWT_SECRET = os.getenv(
    "GUEST_TOKEN_JWT_SECRET",
    os.environ["SUPERSET_SECRET_KEY"],
)

# ---------------------------------------------------------------------------
# Embedding — CORS, Talisman e headers de frame
# ---------------------------------------------------------------------------
# Necessário para que dashboards embarcados (via SDK / iframe) carreguem em
# domínios externos. Defina SUPERSET_CORS_ORIGINS com origens separadas por vírgula.
ENABLE_CORS = _bool_env("SUPERSET_ENABLE_CORS", True)
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "resources": ["*"],
    "origins": _csv_env("SUPERSET_CORS_ORIGINS", ["*"]),
}

# Talisman injeta CSP / HSTS / X-Frame-Options automaticamente e, com defaults,
# bloqueia embed em iframe de terceiros. Desativado aqui para permitir o embed.
TALISMAN_ENABLED = _bool_env("SUPERSET_TALISMAN_ENABLED", False)

# Sobrescreve o X-Frame-Options padrão (SAMEORIGIN) para permitir embedding
# de qualquer origem. Combinado com TALISMAN_ENABLED=False acima.
HTTP_HEADERS = {
    "X-Frame-Options": os.getenv("SUPERSET_X_FRAME_OPTIONS", "ALLOWALL"),
}

# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------
SQLLAB_CTAS_NO_LIMIT = True
MAPBOX_API_KEY = os.environ.get("MAPBOX_API_KEY", "")
WEBDRIVER_BASEURL = os.environ.get("WEBDRIVER_BASEURL", "http://superset_app:8088/")
WEBDRIVER_BASEURL_USER_FRIENDLY = os.environ.get(
    "WEBDRIVER_BASEURL_USER_FRIENDLY", WEBDRIVER_BASEURL
)

log_level_text = os.getenv("SUPERSET_LOG_LEVEL", "INFO")
LOG_LEVEL = getattr(logging, log_level_text.upper(), logging.INFO)
