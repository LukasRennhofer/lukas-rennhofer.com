import html
import re
from dataclasses import dataclass
from pathlib import Path

from cms.codebox.gen import generate_html
from cms.codebox.tokenizer import Lexer, Token

@dataclass
class Post:
	slug: str
	title: str
	body_html: str
	metadata: dict[str, str]
	source_path: Path


def _slugify(value: str) -> str:
	value = value.strip().lower()
	value = re.sub(r"[^a-z0-9]+", "-", value)
	return value.strip("-") or "post"


def _parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
	metadata: dict[str, str] = {}
	lines = content.splitlines()
	if not lines:
		return metadata, content

	if lines[0].strip() != "---":
		return metadata, content

	end_index = None
	for idx in range(1, len(lines)):
		if lines[idx].strip() == "---":
			end_index = idx
			break

	if end_index is None:
		return metadata, content

	for line in lines[1:end_index]:
		if not line.strip() or ":" not in line:
			continue
		key, value = line.split(":", 1)
		metadata[key.strip().lower()] = value.strip()

	body = "\n".join(lines[end_index + 1 :])
	return metadata, body


def get_post_metadata(path: Path) -> dict[str, str]:
	content = path.read_text(encoding="utf-8")
	metadata, _ = _parse_frontmatter(content)
	return metadata


def _format_inline(text: str) -> str:
	link_tokens: list[str] = []

	def replace_link(match: re.Match[str]) -> str:
		label = html.escape(match.group(1).strip())
		href_raw = match.group(2).strip()
		href = html.escape(href_raw, quote=True)
		is_external = href_raw.startswith("http://") or href_raw.startswith("https://")

		token = f"@@LINK{len(link_tokens)}@@"
		if is_external:
			link_tokens.append(
				f'<a href="{href}" target="_blank" rel="noreferrer">{label}</a>'
			)
		else:
			link_tokens.append(f'<a href="{href}">{label}</a>')
		return token

	text_with_links = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", replace_link, text)
	escaped = html.escape(text_with_links)
	escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
	escaped = re.sub(r"__(.+?)__", r"<strong>\1</strong>", escaped)
	escaped = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", escaped)
	escaped = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"<em>\1</em>", escaped)

	for idx, link_html in enumerate(link_tokens):
		escaped = escaped.replace(f"@@LINK{idx}@@", link_html)

	return escaped


def markdown_to_html(markdown: str) -> str:
	lines = markdown.splitlines()
	chunks: list[str] = []

	in_list = False
	in_code_block = False
	code_lines: list[str] = []

	def close_list() -> None:
		nonlocal in_list
		if in_list:
			chunks.append("</ul>")
			in_list = False

	def flush_code_block() -> None:
		nonlocal code_lines

		source = "\n".join(code_lines)

		lexer = Lexer(source)
		tokens = lexer.lex()

		chunks.append(generate_html(tokens))

		code_lines = []

	for raw_line in lines:
		stripped = raw_line.strip()

		# Handle fenced code blocks
		if stripped.startswith("```"):

			if not in_code_block:
				close_list()
				in_code_block = True
				code_lines = []
			else:
				in_code_block = False
				flush_code_block()

			continue

		if in_code_block:
			code_lines.append(raw_line)
			continue

		if not stripped:
			close_list()
			continue

		if re.fullmatch(r"(-{3,}|\*{3,}|_{3,}|={4,})", stripped):
			close_list()
			chunks.append(
				'<div class="post-segment-break" aria-hidden="true"></div>'
			)
			continue

		img_match = re.match(
			r'^!\[([^\]]*)\]\(([^\s)]+)(?:\s+"([^"]+)")?\)$',
			stripped
		)

		if img_match:
			close_list()

			alt_text = html.escape(img_match.group(1))
			img_path = html.escape(img_match.group(2))
			caption = img_match.group(3)

			img_html = (
				f'<figure class="post-image">'
				f'<img decoding="async" src="{img_path}" alt="{alt_text}" />'
			)

			if caption:
				caption_escaped = html.escape(caption)
				img_html += (
					f'<p class="description">{caption_escaped}</p>'
				)

			img_html += "</figure>"
			chunks.append(img_html)

		elif stripped.startswith("### "):
			close_list()
			chunks.append(
				f"<h3>{_format_inline(stripped[4:])}</h3>"
			)

		elif stripped.startswith("## "):
			close_list()
			chunks.append(
				f"<h2>{_format_inline(stripped[3:])}</h2>"
			)

		elif stripped.startswith("# "):
			close_list()
			chunks.append(
				f"<h1>{_format_inline(stripped[2:])}</h1>"
			)

		elif stripped.startswith("- "):
			if not in_list:
				chunks.append("<ul>")
				in_list = True

			chunks.append(
				f"<li>{_format_inline(stripped[2:])}</li>"
			)

		else:
			close_list()
			chunks.append(
				f"<p>{_format_inline(stripped)}</p>"
			)

	# Handle unclosed code block
	if in_code_block:
		flush_code_block()

	close_list()

	return "\n".join(chunks)

def parse_post_file(path: Path) -> Post:
	content = path.read_text(encoding="utf-8")
	metadata, body = _parse_frontmatter(content)
	title = metadata.get("title", "").strip()

	if not title:
		first_non_empty = next((line.strip() for line in body.splitlines() if line.strip()), "")
		title = first_non_empty[:80] if first_non_empty else path.stem.replace("-", " ").title()

	return Post(
		slug=_slugify(path.stem),
		title=title,
		body_html=markdown_to_html(body),
		metadata=metadata,
		source_path=path,
	)
