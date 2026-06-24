import argparse
import sys

import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

BASE_URL = "http://127.0.0.1:8000"  
TIMEOUT = 10                         
console = Console()

def _handle_response_error(response: requests.Response) -> None:

    if response.ok:
        return

    try:
        detail = response.json().get("detail", response.text)
    except Exception:
        detail = response.text

    console.print(
        Panel(
            f"[bold red]HTTP {response.status_code}[/bold red]\n{detail}",
            title="[red]Error[/red]",
            border_style="red",
        )
    )
    sys.exit(1)


def _api_get(path: str, params: dict | None = None) -> dict | list:
    try:
        r = requests.get(f"{BASE_URL}{path}", params=params, timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        console.print(
        )
        sys.exit(1)
    _handle_response_error(r)
    return r.json()


def _api_post(path: str, json: dict) -> dict:
    try:
        r = requests.post(f"{BASE_URL}{path}", json=json, timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        console.print("[bold red]Could not connect to the API.[/bold red]")
        sys.exit(1)
    _handle_response_error(r)
    return r.json()


def _api_patch(path: str, json: dict) -> dict:
    try:
        r = requests.patch(f"{BASE_URL}{path}", json=json, timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        console.print("[bold red]Could not connect to the API.[/bold red]")
        sys.exit(1)
    _handle_response_error(r)
    return r.json()


def _api_delete(path: str) -> None:
    try:
        r = requests.delete(f"{BASE_URL}{path}", timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        console.print("[bold red]Could not connect to the API.[/bold red]")
        sys.exit(1)
    _handle_response_error(r)


_PRIORITY_STYLE = {
    "high":   "bold red",
    "medium": "bold yellow",
    "low":    "bold green",
}


def _priority_badge(priority: str) -> str:
    style = _PRIORITY_STYLE.get(priority.lower(), "white")
    return f"[{style}]{priority.upper()}[/{style}]"


def _completed_badge(completed: bool) -> str:
    return "[green]✔ Done[/green]" if completed else "[dim]○ Pending[/dim]"


def _render_task_table(tasks: list[dict], title: str = "Tasks") -> None:
    """Render a list of task dicts as a rich Table."""
    if not tasks:
        console.print(Panel("[dim]No tasks found.[/dim]", title=title))
        return

    table = Table(
        title=title,
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        border_style="bright_blue",
        highlight=True,
    )
    table.add_column("ID",          style="dim", width=5, justify="right")
    table.add_column("Title",       min_width=24)
    table.add_column("Priority",    width=10, justify="center")
    table.add_column("Status",      width=12, justify="center")
    table.add_column("Created",     width=20, style="dim")

    for task in tasks:
        created = task["created_at"][:19].replace("T", " ") 
        table.add_row(
            str(task["id"]),
            task["title"],
            _priority_badge(task["priority"]),
            _completed_badge(task["completed"]),
            created,
        )

    console.print(table)


def _render_task_detail(task: dict) -> None:
    """Render a single task as a rich Panel with full details."""
    status_text = _completed_badge(task["completed"])
    priority_text = _priority_badge(task["priority"])
    desc = task.get("description") or "[dim]—[/dim]"
    created = task["created_at"][:19].replace("T", " ")

    body = (
        f"[bold]ID:[/bold]          {task['id']}\n"
        f"[bold]Title:[/bold]       {task['title']}\n"
        f"[bold]Description:[/bold] {desc}\n"
        f"[bold]Priority:[/bold]    {priority_text}\n"
        f"[bold]Status:[/bold]      {status_text}\n"
        f"[bold]Created:[/bold]     {created}"
    )
    console.print(
        Panel(body, title=f"[bold cyan]Task #{task['id']}[/bold cyan]", border_style="cyan")
    )



def cmd_add(args: argparse.Namespace) -> None:
    """POST /tasks — create a new task."""
    payload: dict = {"title": args.title, "priority": args.priority}
    if args.desc:
        payload["description"] = args.desc

    task = _api_post("/tasks", payload)
    console.print(
        Panel(
            f"[green]Task created successfully![/green]\n"
            f"[dim]ID {task['id']} · {task['title']}[/dim]",
            border_style="green",
        )
    )
    _render_task_detail(task)


def cmd_list(args: argparse.Namespace) -> None:
    """GET /tasks — list tasks with optional filters."""
    params: dict = {"limit": args.limit, "offset": args.offset}
    if args.priority:
        params["priority"] = args.priority
    if args.completed is not None:
        params["completed"] = args.completed

    data = _api_get("/tasks", params=params)
    total = data.get("total", 0)
    tasks = data.get("tasks", [])

    title = f"All Tasks  [dim]({total} total)[/dim]"
    _render_task_table(tasks, title=title)


def cmd_get(args: argparse.Namespace) -> None:
    """GET /tasks/{id} — show details for a single task."""
    task = _api_get(f"/tasks/{args.id}")
    _render_task_detail(task)


def cmd_complete(args: argparse.Namespace) -> None:
    """PATCH /tasks/{id} — mark a task as completed."""
    task = _api_patch(f"/tasks/{args.id}", {"completed": True})
    console.print(
        Panel(
            f"[green]Task #{args.id} marked as complete.[/green]\n"
            f"[dim]{task['title']}[/dim]",
            border_style="green",
        )
    )


def cmd_update(args: argparse.Namespace) -> None:
    """PATCH /tasks/{id} — update one or more fields of a task."""
    payload: dict = {}
    if args.title:
        payload["title"] = args.title
    if args.desc is not None:
        payload["description"] = args.desc
    if args.priority:
        payload["priority"] = args.priority
    if args.completed is not None:
        payload["completed"] = args.completed

    if not payload:
        console.print("[yellow]Nothing to update — provide at least one flag.[/yellow]")
        sys.exit(0)

    task = _api_patch(f"/tasks/{args.id}", payload)
    console.print(Panel("[green]Task updated.[/green]", border_style="green"))
    _render_task_detail(task)


def cmd_delete(args: argparse.Namespace) -> None:
    """DELETE /tasks/{id} — permanently remove a task."""
    if not args.yes:
        confirm = console.input(
            f"[yellow]Delete task #{args.id}? This cannot be undone. (y/N): [/yellow]"
        )
        if confirm.strip().lower() not in ("y", "yes"):
            console.print("[dim]Deletion cancelled.[/dim]")
            return

    _api_delete(f"/tasks/{args.id}")
    console.print(
        Panel(
            f"[red]Task #{args.id} has been permanently deleted.[/red]",
            border_style="red",
        )
    )

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task-cli",
        description="Task Tracker CLI — manage your tasks from the terminal.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    subparsers.required = True

    # ------------------------------------------------------------------ add
    add_p = subparsers.add_parser("add", help="Create a new task.")
    add_p.add_argument("title", help="Short title for the task (max 120 chars).")
    add_p.add_argument(
        "--priority", "-p",
        choices=["low", "medium", "high"],
        default="medium",
        help="Task urgency (default: medium).",
    )
    add_p.add_argument("--desc", "-d", default=None, help="Optional description.")
    add_p.set_defaults(func=cmd_add)

    list_p = subparsers.add_parser("list", help="List tasks (with optional filters).")
    list_p.add_argument(
        "--priority", "-p",
        choices=["low", "medium", "high"],
        default=None,
        help="Filter by priority.",
    )
    list_p.add_argument(
        "--completed",
        type=lambda x: x.lower() == "true",
        default=None,
        metavar="true|false",
        help="Filter by completion status.",
    )
    list_p.add_argument("--limit", type=int, default=50, help="Max results (default 50).")
    list_p.add_argument("--offset", type=int, default=0, help="Results to skip.")
    list_p.set_defaults(func=cmd_list)

    
    get_p = subparsers.add_parser("get", help="Show details for a single task.")
    get_p.add_argument("id", type=int, help="Task ID.")
    get_p.set_defaults(func=cmd_get)

    comp_p = subparsers.add_parser("complete", help="Mark a task as completed.")
    comp_p.add_argument("id", type=int, help="Task ID.")
    comp_p.set_defaults(func=cmd_complete)

    upd_p = subparsers.add_parser("update", help="Update fields on an existing task.")
    upd_p.add_argument("id", type=int, help="Task ID.")
    upd_p.add_argument("--title", default=None, help="New title.")
    upd_p.add_argument("--desc", default=None, help="New description.")
    upd_p.add_argument(
        "--priority", "-p",
        choices=["low", "medium", "high"],
        default=None,
    )
    upd_p.add_argument(
        "--completed",
        type=lambda x: x.lower() == "true",
        default=None,
        metavar="true|false",
    )
    upd_p.set_defaults(func=cmd_update)

    del_p = subparsers.add_parser("delete", help="Permanently delete a task.")
    del_p.add_argument("id", type=int, help="Task ID.")
    del_p.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip the confirmation prompt.",
    )
    del_p.set_defaults(func=cmd_delete)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
