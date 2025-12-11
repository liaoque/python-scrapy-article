#!/usr/bin/env python3
"""
从CHANGELOG.md中提取指定版本的更新内容

使用方法:
    python release_config/scripts/extract_changelog.py 1.0.0
"""

import sys
import re
from pathlib import Path


def extract_changelog(version: str, changelog_path: Path = None) -> str:
    """从CHANGELOG.md中提取指定版本的更新内容"""
    if changelog_path is None:
        changelog_path = Path(__file__).parent.parent.parent / "CHANGELOG.md"
    
    if not changelog_path.exists():
        return f"CHANGELOG.md not found at {changelog_path}"
    
    content = changelog_path.read_text(encoding='utf-8')
    
    # 匹配版本段落
    pattern = rf'## \[{re.escape(version)}\] - ([^\n]+)\n(.*?)(?=## \[|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return f"Version {version} not found in CHANGELOG.md"
    
    date = match.group(1)
    notes = match.group(2).strip()
    
    # 格式化输出
    result = f"# QuickStock SDK {version} ({date})\n\n{notes}"
    
    return result


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("Usage: python extract_changelog.py <version>")
        print("Example: python extract_changelog.py 1.0.0")
        sys.exit(1)
    
    version = sys.argv[1]
    changelog = extract_changelog(version)
    print(changelog)


if __name__ == "__main__":
    main()