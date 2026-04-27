import argparse

from cms.common import DIST_DIR
from cms.generate import build_site, clean_dist, list_post_files
from cms.post import parse_post_file


def cmd_build(_: argparse.Namespace) -> int:
	created = build_site()
	print(f"Built site in {DIST_DIR}")
	print(f"Generated {len(created)} html file(s).")
	return 0


def cmd_clean(_: argparse.Namespace) -> int:
	clean_dist()
	print(f"Removed {DIST_DIR}")
	return 0


def cmd_list_posts(_: argparse.Namespace) -> int:
	posts = list_post_files()
	if not posts:
		print("No posts found.")
		return 0

	print("Total posts found:", len(posts))
	
	for post in posts:
		post = parse_post_file(post)
		print("================================")
		print(f"Title: {post.title}")
		print(f"Slug: {post.slug}")
		print(f"Source: {post.source_path}")
		print(f"Metadata: {post.metadata}")
		print("================================")

	return 0


def create_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="lrcms", description="Minimal static site CMS")
	subparsers = parser.add_subparsers(dest="command", required=True)

	build_parser = subparsers.add_parser("build", help="Build site into dist/")
	build_parser.set_defaults(func=cmd_build)

	clean_parser = subparsers.add_parser("clean", help="Remove dist/")
	clean_parser.set_defaults(func=cmd_clean)

	list_parser = subparsers.add_parser("list-posts", help="List discovered .post files")
	list_parser.set_defaults(func=cmd_list_posts)

	return parser


def main(argv: list[str] | None = None) -> int:
	parser = create_parser()
	args = parser.parse_args(argv)
	return args.func(args)

