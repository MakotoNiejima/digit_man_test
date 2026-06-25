from pathlib import Path


def load_prompt_template(template_name: str) -> str:
	file_path = Path( __file__ ).parent / 'jinja2' / f"{template_name}.jinja2"
	return file_path.read_text(encoding="utf-8")