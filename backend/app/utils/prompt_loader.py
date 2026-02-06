"""
Prompt Loader using Jinja2 Templates
"""

from pathlib import Path
from functools import lru_cache

from jinja2 import Environment, FileSystemLoader, select_autoescape


PROMPTS_DIR = Path(__file__).parent.parent / "triage" / "prompts"


@lru_cache()
def _get_jinja_env() -> Environment:
    """获取 Jinja2 环境（单例）"""
    return Environment(
        loader=FileSystemLoader(PROMPTS_DIR),
        autoescape=select_autoescape(disabled_extensions=["md"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def load_prompt(filename: str) -> str:
    """
    加载 Jinja2 模板文件

    Args:
        filename: 模板文件名 (如 "classification.md")

    Returns:
        模板内容字符串
    """
    prompt_path = PROMPTS_DIR / filename

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")


def render_prompt(filename: str, **kwargs) -> str:
    """
    渲染 Jinja2 模板

    Args:
        filename: 模板文件名 (如 "classification.md")
        **kwargs: 模板变量

    Returns:
        渲染后的字符串
    """
    env = _get_jinja_env()
    template = env.get_template(filename)
    return template.render(**kwargs)
