from dataclasses import dataclass
from pathlib import Path

from cms.post import markdown_to_html


@dataclass
class ProjectEntry:
	title: str
	description_html: str
	image: str
	link: str
	where: str
	authors: str


def _build_entry(title: str, lines: list[str]) -> ProjectEntry:
	metadata: dict[str, str] = {}
	description_lines: list[str] = []
	in_metadata = True

	for raw_line in lines:
		stripped = raw_line.strip()

		if in_metadata and not stripped:
			in_metadata = False
			continue

		if in_metadata and ":" in raw_line:
			key, value = raw_line.split(":", 1)
			key = key.strip().lower()
			if key in {"image", "link", "where", "authors"}:
				metadata[key] = value.strip()
				continue

		in_metadata = False
		description_lines.append(raw_line)

	description_markdown = "\n".join(description_lines).strip()
	description_html = markdown_to_html(description_markdown) if description_markdown else ""

	return ProjectEntry(
		title=title.strip(),
		description_html=description_html,
		image=metadata.get("image", "").strip(),
		link=metadata.get("link", "").strip(),
		where=metadata.get("where", "").strip(),
		authors=metadata.get("authors", "").strip(),
	)


def parse_project_entries(path: Path) -> list[ProjectEntry]:
	if not path.exists():
		return []

	lines = path.read_text(encoding="utf-8").splitlines()
	entries: list[ProjectEntry] = []
	current_title: str | None = None
	current_lines: list[str] = []

	for raw_line in lines:
		if raw_line.startswith("## "):
			if current_title:
				entries.append(_build_entry(current_title, current_lines))
			current_title = raw_line[3:].strip()
			current_lines = []
			continue

		if current_title is not None:
			current_lines.append(raw_line)

	if current_title:
		entries.append(_build_entry(current_title, current_lines))

	return [entry for entry in entries if entry.title]
