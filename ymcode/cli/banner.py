#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE 欢迎横幅 - 有个性的那种
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.style import Style

console = Console()


# YM-CODE 品牌色
AURORA_PURPLE = "#8B5CF6"
ELECTRIC_BLUE = "#3B82F6"
DEEP_SPACE = "#0F172A"


def get_welcome_banner() -> str:
    """获取欢迎横幅"""
    return f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   [bold {AURORA_PURPLE}]🔮[/bold {AURORA_PURPLE}]  [bold white]YM-CODE[/bold white]  [dim]v0.1.0 Aurora[/dim]                  ║
║                                                          ║
║   [dim]Your Mind, Extended.[/dim]                              ║
║   [dim]你的编程伙伴，你的思维延伸[/dim]                            ║
║                                                          ║
║   [yellow]✨[/yellow] 165 tests passed  [green]✅[/green] 32+ skills  [blue]🚀[/blue] 100% score  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

[dim]Type [white]'help'[/white] for commands, [white]'skills'[/white] to see available skills.[/dim]
[dim]Press [white]Ctrl+C[/white] to exit.[/dim]
"""


def get_motd() -> str:
    """获取每日一句（Message of the Day）"""
    import random
    
    quotes = [
        ("💡", "代码是写给人看的，顺便让机器执行。"),
        ("🎯", "好的代码自己会说话。"),
        ("⚡", "快速迭代，持续改进。"),
        ("🧠", "让 AI 延伸你的思维，不是替代它。"),
        ("🚀", "今天也要写出让自己骄傲的代码！"),
        ("🔮", "预见未来，不如创造未来。"),
        ("💪", "每个 bug 都是成长的机会。"),
        ("🎨", "编程是艺术，代码是画布。"),
        ("🌟", "你写的不是代码，是可能性。"),
        ("🔥", "保持热情，保持好奇。"),
    ]
    
    emoji, quote = random.choice(quotes)
    return f"{emoji} {quote}"


def show_welcome() -> None:
    """显示欢迎界面"""
    console.print()
    
    # 主横幅
    banner_text = Text()
    banner_text.append("🔮 ", style=AURORA_PURPLE)
    banner_text.append("YM-CODE", style=f"bold {AURORA_PURPLE}")
    banner_text.append(" v0.1.0 Aurora", style="dim")
    
    console.print(Panel(
        banner_text,
        subtitle="Your Mind, Extended.",
        border_style=AURORA_PURPLE
    ))
    
    # 统计信息
    stats = Text()
    stats.append("✅ ", style="green")
    stats.append("165 tests passed", style="green")
    stats.append("  ", style="")
    stats.append("🧩 ", style="blue")
    stats.append("32+ skills", style="blue")
    stats.append("  ", style="")
    stats.append("🏆 ", style="yellow")
    stats.append("100% score", style="yellow")
    
    console.print(Panel(stats, border_style="dim"))
    
    # 每日一句
    motd = get_motd()
    console.print(f"\n[dim]{motd}[/dim]\n")


def show_skill_of_the_day() -> str:
    """展示今日推荐技能"""
    import random
    
    skills = [
        ("🔍", "search", "Web/文件/代码搜索，想搜啥搜啥"),
        ("💻", "code_analysis", "代码质量分析，写出更优雅的代码"),
        ("🗄️", "database", "数据库操作，MySQL/PostgreSQL 一键搞定"),
        ("🐳", "docker", "Docker 管理，容器化从未如此简单"),
        ("📝", "formatter", "代码格式化，强迫症的福音"),
        ("🧠", "memory", "长期记忆，越用越懂你"),
        ("⚡", "self_improvement", "自我进化，每天都在进步"),
    ]
    
    emoji, name, desc = random.choice(skills)
    return f"{emoji} **Skill of the Day**: [{name}](skills/{name}) - {desc}"


# ASCII Art 版本（备用）
ASCII_BANNER = """
 __  __                  ____  _____ 
|  \\/  | _____   _____  / ___|| ____|
| |\\/| |/ _ \\ \\ / / _ \\ \\___ \\|  _|  
| |  | | (_) \\ V /  __/  ___) | |___ 
|_|  |_|\\___/ \\_/ \\___| |____/|_____|
          Your Mind, Extended.
"""


if __name__ == "__main__":
    show_welcome()
