"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use when you need to inspect files, read instructions, docstrings, logs, or sample data, "
                "and report findings without modifying any files."
            ),
            "system_prompt": (
                "You are an exploration subagent. Inspect repository files, search for code/data patterns, "
                "read docstrings and instructions, and return an accurate factual report. Do not modify any files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use when you need to perform code edits, process data, run scripts or tests, and verify implementation results."
            ),
            "system_prompt": (
                "You are an implementation subagent. Make code or data changes according to specifications, "
                "execute scripts or tests in the shell, and report execution results back to the main agent."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use when you need to independently verify changes, test edge cases, and check output format against requirements."
            ),
            "system_prompt": (
                "You are a reviewer subagent. Inspect modified files and outputs against requirements and edge cases, "
                "and report any discrepancies without modifying files."
            ),
        },
    ]
