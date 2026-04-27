from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Source directories
CMS_DIR = PROJECT_ROOT / "cms"
SITE_DIR = PROJECT_ROOT / "site"
COMPONENTS_DIR = SITE_DIR / "components"
CSS_DIR = SITE_DIR / "css"
JS_DIR = SITE_DIR / "js"
ASSETS_DIR = PROJECT_ROOT / "assets"
POSTS_DIR = PROJECT_ROOT / "posts"
PROJECTS_DIR = PROJECT_ROOT / "projects"
NEWS_DIR = PROJECT_ROOT / "news"

# Build output directories
DIST_DIR = PROJECT_ROOT / "dist"
DIST_ASSETS_DIR = DIST_DIR / "assets"
DIST_POSTS_RAW_DIR = DIST_DIR / "posts"
DIST_BLOG_DIR = DIST_DIR / "blog"
DIST_PROJECTS_DIR = DIST_DIR / "projects"
DIST_PROJECT_ALIAS_DIR = DIST_DIR / "project"

# Component file names
HEADER_COMPONENT_NAME = "header.html"
NAV_COMPONENT_NAME = "nav.html"
FOOTER_COMPONENT_NAME = "footer.html"
META_COMPONENT_NAME = "meta.html"
START_COMPONENT_NAME = "start_site.html"
SITE_IN_WORK_COMPONENT_NAME = "site_in_work.html"
ABOUT_COMPONENT_NAME = "about/about.html"

# Post format and output names
POST_EXTENSION = ".post"
PROJECT_EXTENSION = ".project"
NEWS_FILE_NAME = "news.news"
INDEX_FILE_NAME = "index.html"
