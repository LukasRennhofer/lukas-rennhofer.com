from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from cms.post import markdown_to_html


@dataclass
class NewsItem:
	date_text: str
	date_value: datetime
	text_html: str


def _parse_date(value: str) -> datetime:
	value = value.strip()
	formats = (
		"%Y-%m-%d",
		"%Y/%m/%d",
		"%d.%m.%Y",
		"%d %b %Y",
	)
	for fmt in formats:
		try:
			return datetime.strptime(value, fmt)
		except ValueError:
			continue
	return datetime.min


def parse_news_file(path: Path) -> list[NewsItem]:
	if not path.exists():
		return []

	lines = path.read_text(encoding="utf-8").splitlines()
	items: list[NewsItem] = []
	current_date = ""
	current_lines: list[str] = []

	def flush() -> None:
		nonlocal current_date, current_lines
		if not current_date:
			return
		text_markdown = "\n".join(current_lines).strip()
		text_html = markdown_to_html(text_markdown) if text_markdown else ""
		items.append(
			NewsItem(
				date_text=current_date,
				date_value=_parse_date(current_date),
				text_html=text_html,
			)
		)
		current_date = ""
		current_lines = []

	for raw in lines:
		if raw.startswith("## "):
			flush()
			current_date = raw[3:].strip()
			continue
		if current_date:
			current_lines.append(raw)

	flush()
	items.sort(key=lambda item: item.date_value, reverse=True)
	return items
