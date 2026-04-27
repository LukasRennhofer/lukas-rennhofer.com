import html
import shutil
from datetime import datetime
from pathlib import Path

from cms.common import (
	ASSETS_DIR,
	ABOUT_COMPONENT_NAME,
	COMPONENTS_DIR,
	CSS_DIR,
	DIST_ASSETS_DIR,
	DIST_BLOG_DIR,
	DIST_DIR,
	DIST_PROJECTS_DIR,
	DIST_PROJECT_ALIAS_DIR,
	DIST_POSTS_RAW_DIR,
	FOOTER_COMPONENT_NAME,
	HEADER_COMPONENT_NAME,
	INDEX_FILE_NAME,
	JS_DIR,
	META_COMPONENT_NAME,
	NAV_COMPONENT_NAME,
	NEWS_DIR,
	NEWS_FILE_NAME,
	PROJECTS_DIR,
	POST_EXTENSION,
	POSTS_DIR,
	SITE_IN_WORK_COMPONENT_NAME,
	START_COMPONENT_NAME,
)
from cms.news import NewsItem, parse_news_file
from cms.project import ProjectEntry, parse_project_entries
from cms.post import parse_post_file


def _read_component(name: str) -> str:
	path = COMPONENTS_DIR / name
	if not path.exists():
		return ""
	return path.read_text(encoding="utf-8")


def _render_page(title: str, main_content: str) -> str:
	header = _read_component(HEADER_COMPONENT_NAME)
	nav = _read_component(NAV_COMPONENT_NAME)
	footer = _read_component(FOOTER_COMPONENT_NAME)
	meta = _read_component(META_COMPONENT_NAME)

	return f"""<!doctype html>
<html lang=\"en\">
<head>
  <title>{html.escape(title)}</title>
<link rel=\"stylesheet\" href=\"/css/fonts.css\" />
<link rel=\"stylesheet\" href=\"/css/site.css\" />
<script src=\"/js/site.js\" defer></script>
{meta}
</head>
<body>
{header}
{nav}
<main class=\"content\">{main_content}</main>
{footer}
</body>
</html>
"""


def _parse_post_datetime(post) -> datetime:
	date_text = (
		post.metadata.get("date")
		or post.metadata.get("published")
		or post.metadata.get("published_at")
		or ""
	).strip()

	formats = (
		"%Y-%m-%d",
		"%Y/%m/%d",
		"%Y-%m-%d %H:%M",
		"%Y-%m-%d %H:%M:%S",
		"%Y-%m-%dT%H:%M",
		"%Y-%m-%dT%H:%M:%S",
		"%Y",
	)

	for fmt in formats:
		try:
			return datetime.strptime(date_text, fmt)
		except ValueError:
			continue

	return datetime.fromtimestamp(post.source_path.stat().st_mtime)


def _parse_post_tags(post) -> list[str]:
	raw = (post.metadata.get("tags") or post.metadata.get("tag") or "").strip()
	if not raw:
		return []

	tags = [part.strip() for part in raw.replace(";", ",").split(",")]
	return [tag for tag in tags if tag]


def _render_post_meta(post) -> str:
	date_label = _parse_post_datetime(post).strftime("%d %b %Y")
	tags = _parse_post_tags(post)
	tags_label = ", ".join(html.escape(tag) for tag in tags)

	meta_line = html.escape(date_label)
	if tags_label:
		meta_line = f"{meta_line} | Tags: {tags_label}"

	return f'<div class="post-meta"><p class="post-date">{meta_line}</p></div>'


def _render_post_page(post) -> str:
	meta_html = _render_post_meta(post)

	return (
		f'<article class="post-page">'
		f'<header class="post-page-header">'
		f'<h1 class="post-title">{html.escape(post.title)}</h1>'
		f'{meta_html}'
		f'</header>'
		f'<section class="post-content">{post.body_html}</section>'
		f'</article>'
	)


def _render_blog_subnav(active: str) -> str:
	blog_class = "is-active" if active == "blog" else ""
	news_class = "is-active" if active == "news" else ""
	archive_class = "is-active" if active == "archive" else ""
	return f"""
<nav class="blog-subnav" aria-label="Blog sections">
  <a class="{blog_class}" href="/blog/">Blog</a>
  <a class="{news_class}" href="/blog/news/">News</a>
  <a class="{archive_class}" href="/blog/archive/">Archive</a>
</nav>
"""


def _render_projects_subnav(active: str) -> str:
	personal_class = "is-active" if active == "personal" else ""
	career_class = "is-active" if active == "career" else ""
	publications_class = "is-active" if active == "publications" else ""
	return f"""
<nav class="blog-subnav projects-subnav" aria-label="Projects sections">
  <a class="{personal_class}" href="/projects/">Personal Work</a>
  <a class="{career_class}" href="/projects/career/">Career</a>
  <a class="{publications_class}" href="/projects/publications/">Publications</a>
</nav>
"""


def _render_projects_entries(entries: list[ProjectEntry], include_publication_meta: bool) -> str:
	if not entries:
		return '<section class="projects-list"><p>No entries yet.</p></section>'

	parts = []
	for entry in entries:
		image_html = ""
		if entry.image:
			image_html = (
				f'<img src="{html.escape(entry.image)}" alt="{html.escape(entry.title)}" loading="lazy" />'
			)

		meta_lines: list[str] = []
		if include_publication_meta and entry.where:
			meta_lines.append(
				f'<p class="project-item-meta"><strong>Presented at:</strong> {html.escape(entry.where)}</p>'
			)
		if include_publication_meta and entry.authors:
			meta_lines.append(
				f'<p class="project-item-meta"><strong>Authors:</strong> {html.escape(entry.authors)}</p>'
			)

		link_html = ""
		if entry.link:
			link_html = (
				f'<p class="project-item-link"><a href="{html.escape(entry.link)}" target="_blank" rel="noreferrer">Open link</a></p>'
			)

		description_html = entry.description_html or ""
		parts.append(
			(
				'<article class="project-item">'
				f'<div class="project-item-image">{image_html}</div>'
				'<div class="project-item-body">'
				f'<h2 class="project-item-title">{html.escape(entry.title)}</h2>'
				f'{"".join(meta_lines)}'
				f'<div class="project-item-description">{description_html}</div>'
				f'{link_html}'
				'</div>'
				'</article>'
			)
		)

	return f'<section class="projects-list">{"".join(parts)}</section>'


def _render_projects_page(active: str, entries: list[ProjectEntry], include_publication_meta: bool) -> str:
	subnav = _render_projects_subnav(active)
	body = _render_projects_entries(entries, include_publication_meta)
	return f"{subnav}{body}"

def _render_news_entries(items: list[NewsItem], limit: int | None = None, compact: bool = False) -> str:
	if not items:
		return '<section class="news-list"><p>No news yet.</p></section>'

	entries = items[:limit] if limit is not None else items
	parts = []
	for item in entries:
		date_label = item.date_text
		if item.date_value != datetime.min:
			date_label = item.date_value.strftime("%d %b %Y")

		parts.append(
			(
				'<article class="news-item">'
				f'<p class="news-item-date">{html.escape(date_label)}</p>'
				f'<div class="news-item-text">{item.text_html}</div>'
				'</article>'
			)
		)

	more_link = ''
	if compact and len(items) > len(entries):
		more_link = '<p class="news-more"><a href="/blog/">More news</a></p>'

	css_class = 'news-list news-list-compact' if compact else 'news-list news-list-page'
	return f'<section class="{css_class}">{"".join(parts)}{more_link}</section>'


def _render_home_news(items: list[NewsItem]) -> str:
	body = _render_news_entries(items, limit=3, compact=True)
	return f'<aside class="home-news" aria-label="Latest news">{body}</aside>'


def _render_blog_posts(posts: list) -> str:
	if not posts:
		return _render_blog_subnav("blog") + "<section class=\"blog-feed\"><p>No posts yet.</p></section>"

	sorted_posts = sorted(posts, key=_parse_post_datetime, reverse=True)
	feed_parts = []
	for post in sorted_posts:
		meta_html = _render_post_meta(post)
		feed_parts.append(
			"""
			<article class="blog-feed-post">
			  <header class="post-page-header">
			    <h2 class="post-title"><a href="/blog/{slug}/">{title}</a></h2>
			    {meta}
			  </header>
			  <section class="post-content">{body}</section>
			</article>
			""".format(
				slug=html.escape(post.slug),
				title=html.escape(post.title),
				meta=meta_html,
				body=post.body_html,
			)
		)

	return _render_blog_subnav("blog") + f"<section class=\"blog-feed\">{''.join(feed_parts)}</section>"


def _render_blog_news(items: list[NewsItem]) -> str:
	return _render_blog_subnav("news") + _render_news_entries(items)


def _render_blog_archive(posts: list) -> str:
	if not posts:
		return _render_blog_subnav("archive") + "<section class=\"blog-archive-nav\"><p>No posts yet.</p></section>"

	sorted_posts = sorted(posts, key=_parse_post_datetime, reverse=True)
	grouped: dict[int, list] = {}
	for post in sorted_posts:
		year = _parse_post_datetime(post).year
		grouped.setdefault(year, []).append(post)

	years_desc = sorted(grouped.keys(), reverse=True)
	archive_parts = []
	for year in years_desc:
		post_links = "".join(
			(
				'<li class="blog-archive-item">'
				f'<a href="/blog/{html.escape(p.slug)}/">{html.escape(p.title)}</a>'
				f'<span class="blog-archive-date">{_parse_post_datetime(p).strftime("%d %b %Y")}</span>'
				"</li>"
			)
			for p in grouped[year]
		)
		archive_parts.append(
			f'<section class="blog-archive-year"><h2 class="blog-year-heading">{year}</h2><ul class="blog-archive-list">{post_links}</ul></section>'
		)

	return _render_blog_subnav("archive") + f"<section class=\"blog-archive-nav\">{''.join(archive_parts)}</section>"


def _copy_if_exists(source: Path, destination: Path) -> None:
	if not source.exists():
		return
	shutil.copytree(source, destination, dirs_exist_ok=True)


def _write_text(path: Path, content: str) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(content, encoding="utf-8")


def clean_dist() -> None:
	if DIST_DIR.exists():
		shutil.rmtree(DIST_DIR)


def build_site() -> list[Path]:
	clean_dist()
	DIST_DIR.mkdir(parents=True, exist_ok=True)
	DIST_BLOG_DIR.mkdir(parents=True, exist_ok=True)
	DIST_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

	_copy_if_exists(ASSETS_DIR, DIST_ASSETS_DIR)
	_copy_if_exists(POSTS_DIR, DIST_POSTS_RAW_DIR)
	_copy_if_exists(CSS_DIR, DIST_DIR / "css")
	_copy_if_exists(JS_DIR, DIST_DIR / "js")

	created_files = []
	posts = []
	for post_path in sorted(POSTS_DIR.glob(f"*{POST_EXTENSION}")):
		post = parse_post_file(post_path)
		posts.append(post)

		post_html = _render_post_page(post)
		out_path = DIST_BLOG_DIR / post.slug / INDEX_FILE_NAME
		_write_text(out_path, _render_page(post.title, post_html))
		created_files.append(out_path)

	# Build start page
	news_items = parse_news_file(NEWS_DIR / NEWS_FILE_NAME)
	start_site = _read_component(START_COMPONENT_NAME)
	start_site = start_site.replace("{{HOME_NEWS}}", _render_home_news(news_items))

	index_path = DIST_DIR / INDEX_FILE_NAME
	_write_text(index_path, _render_page("Home", start_site))
	created_files.append(index_path)

	# Build about page
	about_markup = _read_component(ABOUT_COMPONENT_NAME)
	about_path = DIST_DIR / "about" / INDEX_FILE_NAME
	_write_text(about_path, _render_page("About", about_markup))
	created_files.append(about_path)

	# Build temporary projects placeholder page
	site_in_work = _read_component(SITE_IN_WORK_COMPONENT_NAME)
	site_in_work_path = DIST_DIR / "site-in-work" / INDEX_FILE_NAME
	_write_text(site_in_work_path, _render_page("Projects In Progress", site_in_work))
	created_files.append(site_in_work_path)

	# Build blog posts page
	blog_markup = _render_blog_posts(posts)
	blog_index_path = DIST_BLOG_DIR / INDEX_FILE_NAME
	_write_text(blog_index_path, _render_page("Blog", blog_markup))
	created_files.append(blog_index_path)

	# Build blog news page
	news_markup = _render_blog_news(news_items)
	news_index_path = DIST_BLOG_DIR / "news" / INDEX_FILE_NAME
	_write_text(news_index_path, _render_page("News", news_markup))
	created_files.append(news_index_path)

	# Build archive page
	archive_markup = _render_blog_archive(posts)
	archive_index_path = DIST_BLOG_DIR / "archive" / INDEX_FILE_NAME
	_write_text(archive_index_path, _render_page("Blog Archive", archive_markup))
	created_files.append(archive_index_path)

	# Build projects pages
	personal_entries = parse_project_entries(PROJECTS_DIR / "personal.project")
	career_entries = parse_project_entries(PROJECTS_DIR / "career.project")
	publication_entries = parse_project_entries(PROJECTS_DIR / "publications.project")

	projects_index_markup = _render_projects_page("personal", personal_entries, False)
	projects_index_path = DIST_PROJECTS_DIR / INDEX_FILE_NAME
	_write_text(projects_index_path, _render_page("Projects", projects_index_markup))
	created_files.append(projects_index_path)

	personal_index_path = DIST_PROJECTS_DIR / "personal-work" / INDEX_FILE_NAME
	_write_text(personal_index_path, _render_page("Personal Work", projects_index_markup))
	created_files.append(personal_index_path)

	career_markup = _render_projects_page("career", career_entries, False)
	career_index_path = DIST_PROJECTS_DIR / "career" / INDEX_FILE_NAME
	_write_text(career_index_path, _render_page("Career", career_markup))
	created_files.append(career_index_path)

	publications_markup = _render_projects_page("publications", publication_entries, True)
	publications_index_path = DIST_PROJECTS_DIR / "publications" / INDEX_FILE_NAME
	_write_text(publications_index_path, _render_page("Publications", publications_markup))
	created_files.append(publications_index_path)

	# Alias /project/ to main projects landing page.
	project_alias_path = DIST_PROJECT_ALIAS_DIR / INDEX_FILE_NAME
	_write_text(project_alias_path, _render_page("Projects", projects_index_markup))
	created_files.append(project_alias_path)

	return created_files


def list_post_files() -> list[Path]:
	if not POSTS_DIR.exists():
		return []
	return sorted(POSTS_DIR.glob(f"*{POST_EXTENSION}"))
