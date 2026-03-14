#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库系统 CLI 命令
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.markdown import Markdown

from .base import KnowledgeGraph, KnowledgeEntry, KnowledgeType
from .indexer import DocumentIndexer
from .retriever import KnowledgeRetriever

console = Console()


@click.group()
def knowledge():
    """知识库系统命令"""
    pass


# ========== 索引命令 ==========

@knowledge.group()
def index():
    """索引管理命令"""
    pass


@index.command('file')
@click.argument('file_path')
@click.option('--auto-categorize/--no-auto-categorize', default=True)
def index_file(file_path, auto_categorize):
    """索引单个文件"""
    from pathlib import Path
    
    indexer = DocumentIndexer()
    entry = indexer.index_file(Path(file_path), auto_categorize)
    
    if entry:
        console.print(f"[green]✅ 已索引：{entry.title}[/green]")
        console.print(f"分类：{entry.category}")
        console.print(f"标签：{', '.join(entry.tags[:10])}")
    else:
        console.print("[red]❌ 索引失败[/red]")


@index.command('dir')
@click.argument('dir_path')
@click.option('--pattern', '-p', default='*.md')
@click.option('--exclude', '-e', multiple=True)
def index_dir(dir_path, pattern, exclude):
    """索引目录"""
    from pathlib import Path
    
    indexer = DocumentIndexer()
    count = indexer.index_directory(
        Path(dir_path),
        pattern=pattern,
        exclude=list(exclude)
    )
    
    console.print(f"[green]✅ 索引完成：{count} 个文件[/green]")
    
    # 显示统计
    stats = indexer.get_statistics()
    console.print(f"总关键词：{stats['total_keywords']}")


# ========== 搜索命令 ==========

@knowledge.command('search')
@click.argument('query')
@click.option('--category', '-c', default=None)
@click.option('--tag', '-t', multiple=True)
@click.option('--limit', '-l', default=10)
def knowledge_search(query, category, tag, limit):
    """搜索知识"""
    graph = KnowledgeGraph()
    retriever = KnowledgeRetriever(graph)
    
    results = retriever.search(
        query,
        category=category,
        tags=list(tag),
        limit=limit
    )
    
    if not results:
        console.print("[yellow]⚠️ 没有找到相关知识[/yellow]")
        return
    
    console.print(f"\n[bold]找到 {len(results)} 个相关知识：[/bold]\n")
    
    for i, result in enumerate(results, 1):
        console.print(Panel(
            f"[bold cyan]{i}. {result.entry.title}[/bold cyan]\n\n"
            f"[dim]分类：[/dim] {result.entry.category}\n"
            f"[dim]标签：[/dim] {', '.join(result.entry.tags[:5])}\n"
            f"[dim]相关性：[/dim] {result.score:.2f}\n\n"
            f"{result.entry.summary[:200]}...",
            title=f"📚 结果 {i}",
            border_style="blue"
        ))


# ========== 知识管理命令 ==========

@knowledge.group()
def entry():
    """知识条目管理命令"""
    pass


@entry.command('list')
@click.option('--category', '-c', default=None)
@click.option('--limit', '-l', default=20)
def entry_list(category, limit):
    """列出知识条目"""
    graph = KnowledgeGraph()
    
    entries = list(graph.nodes.values())
    
    if category:
        entries = [e for e in entries if e.category == category]
    
    entries = entries[:limit]
    
    if not entries:
        console.print("[yellow]⚠️ 没有知识条目[/yellow]")
        return
    
    table = Table(title="📚 知识条目")
    table.add_column("ID", style="cyan")
    table.add_column("标题", style="green")
    table.add_column("分类", style="magenta")
    table.add_column("类型", style="yellow")
    table.add_column("使用次数", style="blue")
    
    for entry in entries:
        table.add_row(
            entry.id[:8] + "...",
            entry.title[:30],
            entry.category,
            entry.type.value,
            str(entry.usage_count)
        )
    
    console.print(table)


@entry.command('show')
@click.argument('entry_id')
def entry_show(entry_id):
    """显示知识条目详情"""
    graph = KnowledgeGraph()
    
    if entry_id not in graph.nodes:
        console.print(f"[red]❌ 条目不存在：{entry_id}[/red]")
        return
    
    entry = graph.nodes[entry_id]
    
    console.print()
    console.print(Panel(
        f"[bold cyan]{entry.title}[/bold cyan]\n\n"
        f"[dim]ID:[/dim] {entry.id}\n"
        f"[dim]分类:[/dim] {entry.category}\n"
        f"[dim]类型:[/dim] {entry.type.value}\n"
        f"[dim]标签:[/dim] {', '.join(entry.tags)}\n"
        f"[dim]使用次数:[/dim] {entry.usage_count}\n"
        f"[dim]置信度:[/dim] {entry.confidence:.2f}\n\n"
        f"[bold]摘要：[/bold]\n{entry.summary}\n\n"
        f"[bold]内容：[/bold]\n{entry.content[:500]}...",
        title="📖 知识详情",
        border_style="cyan"
    ))


@entry.command('add-relation')
@click.argument('from_id')
@click.argument('to_id')
def entry_add_relation(from_id, to_id):
    """添加知识关联"""
    graph = KnowledgeGraph()
    
    if from_id not in graph.nodes or to_id not in graph.nodes:
        console.print("[red]❌ 条目不存在[/red]")
        return
    
    graph.add_relation(from_id, to_id)
    console.print(f"[green]✅ 已添加关联：{from_id} <-> {to_id}[/green]")


# ========== 分类命令 ==========

@knowledge.group()
def category():
    """分类管理命令"""
    pass


@category.command('tree')
def category_tree():
    """显示分类树"""
    graph = KnowledgeGraph()
    
    tree = Tree("📁 知识分类")
    
    for cat_id, category in graph.categories.items():
        if not category.parent:  # 根分类
            branch = tree.add(f"📂 {category.name}")
            for child_id in category.children:
                if child_id in graph.categories:
                    branch.add(f"📄 {graph.categories[child_id].name}")
    
    console.print(tree)


@category.command('stats')
def category_stats():
    """显示分类统计"""
    graph = KnowledgeGraph()
    stats = graph.get_statistics()
    
    console.print()
    console.print(Panel(
        f"[bold]总条目数：[/bold] {stats['total_entries']}\n"
        f"[bold]总分类数：[/bold] {stats['total_categories']}\n"
        f"[bold]总关联数：[/bold] {stats['total_relations']}\n\n"
        f"[bold]按类型分布：[/bold]\n" +
        '\n'.join([f"  {k}: {v}" for k, v in stats['by_type'].items()]) +
        "\n\n[bold]Top 标签：[/bold]\n" +
        '\n'.join([f"  #{tag}: {count}" for tag, count in stats['top_tags'][:5]]),
        title="📊 知识库统计",
        border_style="green"
    ))


# ========== 推荐命令 ==========

@knowledge.command('related')
@click.argument('entry_id')
@click.option('--limit', '-l', default=5)
def knowledge_related(entry_id, limit):
    """推荐相关知识"""
    graph = KnowledgeGraph()
    retriever = KnowledgeRetriever(graph)
    
    results = retriever.get_related_knowledge(entry_id, limit=limit)
    
    if not results:
        console.print("[yellow]⚠️ 没有相关知识[/yellow]")
        return
    
    console.print(f"\n[bold]相关知识（{len(results)} 个）：[/bold]\n")
    
    for i, result in enumerate(results, 1):
        console.print(
            f"{i}. [cyan]{result.entry.title}[/cyan] "
            f"[dim]({result.score:.2f})[/dim]"
        )


@knowledge.command('popular')
@click.option('--category', '-c', default=None)
@click.option('--limit', '-l', default=10)
def knowledge_popular(category, limit):
    """显示热门知识"""
    graph = KnowledgeGraph()
    retriever = KnowledgeRetriever(graph)
    
    entries = retriever.get_popular_knowledge(category=category, limit=limit)
    
    if not entries:
        console.print("[yellow]⚠️ 没有热门知识[/yellow]")
        return
    
    console.print(f"\n[bold]热门知识：[/bold]\n")
    
    for i, entry in enumerate(entries, 1):
        console.print(
            f"{i}. [cyan]{entry.title}[/cyan] "
            f"[dim]({entry.usage_count} 次使用)[/dim]"
        )


@knowledge.command('recent')
@click.option('--limit', '-l', default=10)
def knowledge_recent(limit):
    """显示最近知识"""
    graph = KnowledgeGraph()
    
    entries = graph.nodes.values()
    entries = sorted(entries, key=lambda x: x.updated_at, reverse=True)[:limit]
    
    if not entries:
        console.print("[yellow]⚠️ 没有最近知识[/yellow]")
        return
    
    console.print(f"\n[bold]最近更新：[/bold]\n")
    
    for i, entry in enumerate(entries, 1):
        console.print(
            f"{i}. [cyan]{entry.title}[/cyan] "
            f"[dim]({entry.updated_at.split('T')[0]})[/dim]"
        )


# 主 CLI 集成
@click.group()
def cli():
    """YM-CODE Knowledge CLI"""
    pass


cli.add_command(knowledge)
cli.add_command(index)
cli.add_command(entry)
cli.add_command(category)


if __name__ == '__main__':
    cli()
