"""
Comprehensive TUI (Text User Interface) for Model Training Application.

Features:
- Screen-based navigation (Home, Projects, XML Editor, Generation, Training)
- Interactive forms and inputs
- Real-time training metrics with sparklines
- Progress tracking for generation and training
- Keyboard shortcuts and mouse support
- Color-coded status indicators
"""

import asyncio
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import requests
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen, ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Log,
    ProgressBar,
    Select,
    Static,
    TextArea,
    TabbedContent,
    TabPane,
    Rule,
)
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel
from rich.table import Table as RichTable


# API Configuration
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")


# ============================================================================
# API Client
# ============================================================================


class APIClient:
    """Client for interacting with the backend API."""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or API_BASE_URL

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, timeout=10)
            else:
                return {"success": False, "error": f"Invalid method: {method}"}

            response.raise_for_status()
            return response.json() if response.text else {"success": True}
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to API. Is the server running?",
            }
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out"}
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                return {
                    "success": False,
                    "error": error_data.get("detail", str(e)),
                }
            except:
                return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Project endpoints
    def list_projects(self) -> Dict[str, Any]:
        """List all projects."""
        return self._make_request("GET", "/projects")

    def get_project(self, name: str) -> Dict[str, Any]:
        """Get project by name."""
        return self._make_request("GET", f"/projects/{name}")

    def create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new project."""
        return self._make_request("POST", "/projects", data)

    def update_project(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing project."""
        return self._make_request("PUT", f"/projects/{name}", data)

    def delete_project(self, name: str) -> Dict[str, Any]:
        """Delete project."""
        return self._make_request("DELETE", f"/projects/{name}")

    # Generation endpoints
    def generate_dataset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate synthetic dataset."""
        return self._make_request("POST", "/generate", data)

    # Training endpoints
    def start_training(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Start training job."""
        return self._make_request("POST", "/train", data)

    def get_training_status(self, job_id: str) -> Dict[str, Any]:
        """Get training job status."""
        return self._make_request("GET", f"/train/status/{job_id}")

    def cancel_training(self, job_id: str) -> Dict[str, Any]:
        """Cancel training job."""
        return self._make_request("DELETE", f"/train/cancel/{job_id}")


# ============================================================================
# Modal Dialogs
# ============================================================================


class ConfirmDialog(ModalScreen[bool]):
    """Modal dialog for confirmations."""

    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }

    ConfirmDialog > Container {
        width: 60;
        height: 11;
        border: thick $background 80%;
        background: $surface;
    }

    ConfirmDialog > Container > Label {
        width: 100%;
        height: 3;
        content-align: center middle;
    }

    ConfirmDialog > Container > Horizontal {
        width: 100%;
        height: auto;
        align: center middle;
    }

    ConfirmDialog Button {
        margin: 1 2;
    }
    """

    def __init__(self, message: str, title: str = "Confirm"):
        super().__init__()
        self.message = message
        self.title = title

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(self.message)
            with Horizontal():
                yield Button("Yes", variant="success", id="yes")
                yield Button("No", variant="error", id="no")

    @on(Button.Pressed, "#yes")
    def handle_yes(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#no")
    def handle_no(self) -> None:
        self.dismiss(False)


class MessageDialog(ModalScreen[None]):
    """Modal dialog for messages."""

    DEFAULT_CSS = """
    MessageDialog {
        align: center middle;
    }

    MessageDialog > Container {
        width: 60;
        height: 11;
        border: thick $background 80%;
        background: $surface;
    }

    MessageDialog > Container > Label {
        width: 100%;
        height: 5;
        content-align: center middle;
    }

    MessageDialog Button {
        width: 20;
        margin: 0 20;
    }
    """

    def __init__(self, message: str, title: str = "Message", variant: str = "primary"):
        super().__init__()
        self.message = message
        self.title = title
        self.variant = variant

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(self.message)
            yield Button("OK", variant=self.variant, id="ok")

    @on(Button.Pressed, "#ok")
    def handle_ok(self) -> None:
        self.dismiss()


# ============================================================================
# Home Screen
# ============================================================================


class HomeScreen(Screen):
    """Main home screen with overview and quick actions."""

    BINDINGS = [
        Binding("p", "show_projects", "Projects"),
        Binding("x", "show_xml", "XML Editor"),
        Binding("g", "show_generation", "Generate"),
        Binding("t", "show_training", "Training"),
        Binding("e", "show_export", "Export"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(
                "[bold cyan]Model Training TUI[/bold cyan]\n\n"
                "[yellow]Welcome to the Model Training Text User Interface![/yellow]\n\n"
                "Quick Actions:\n"
                "  [bold]P[/bold] - Manage Projects\n"
                "  [bold]X[/bold] - Edit XML Patterns\n"
                "  [bold]G[/bold] - Generate Datasets\n"
                "  [bold]T[/bold] - Train Models\n"
                "  [bold]E[/bold] - Export Models\n"
                "  [bold]Q[/bold] - Quit Application\n\n"
                "[dim]Press the corresponding key or use the footer menu[/dim]",
                id="welcome",
            )
        )
        yield Footer()

    def action_show_projects(self) -> None:
        """Switch to projects screen."""
        self.app.push_screen("projects")

    def action_show_xml(self) -> None:
        """Switch to XML editor screen."""
        self.app.push_screen("xml_editor")

    def action_show_generation(self) -> None:
        """Switch to generation screen."""
        self.app.push_screen("generation")

    def action_show_training(self) -> None:
        """Switch to training screen."""
        self.app.push_screen("training")

    def action_show_export(self) -> None:
        """Switch to export screen."""
        self.app.push_screen("export")

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


# ============================================================================
# Projects Screen
# ============================================================================


class ProjectScreen(Screen):
    """Screen for managing projects."""

    BINDINGS = [
        Binding("n", "new_project", "New"),
        Binding("l", "load_project", "Load"),
        Binding("d", "delete_project", "Delete"),
        Binding("r", "refresh", "Refresh"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.selected_project = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("[bold]Project Management[/bold]", id="project_title"),
            DataTable(id="projects_table"),
            Horizontal(
                Button("New Project", variant="success", id="btn_new"),
                Button("Load Project", variant="primary", id="btn_load"),
                Button("Delete Project", variant="error", id="btn_delete"),
                Button("Refresh", variant="default", id="btn_refresh"),
                id="project_buttons",
            ),
            Static("", id="project_status"),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen."""
        table = self.query_one("#projects_table", DataTable)
        table.add_columns("Name", "Objective", "Base Model", "Datasets", "Created")
        table.cursor_type = "row"
        self.action_refresh()

    def action_refresh(self) -> None:
        """Refresh projects list."""
        table = self.query_one("#projects_table", DataTable)
        table.clear()

        result = self.api_client.list_projects()
        if "error" in result:
            self.update_status(f"[red]Error: {result['error']}[/red]")
            return

        projects = result.get("projects", [])
        for project in projects:
            table.add_row(
                project["name"],
                project["objective"][:50] + "..."
                if len(project["objective"]) > 50
                else project["objective"],
                project.get("base_model", "N/A"),
                str(len(project.get("datasets", []))),
                project.get("created_at", "N/A")[:10],
                key=project["name"],
            )

        self.update_status(f"[green]Loaded {len(projects)} project(s)[/green]")

    def action_new_project(self) -> None:
        """Create new project."""
        self.app.push_screen("project_create")

    def action_load_project(self) -> None:
        """Load selected project."""
        table = self.query_one("#projects_table", DataTable)
        if table.cursor_row is not None:
            row_key = table.get_row_at(table.cursor_row)
            if row_key:
                project_name = row_key[0]
                self.selected_project = project_name
                self.app.push_screen("xml_editor")
        else:
            self.update_status("[yellow]No project selected[/yellow]")

    async def action_delete_project(self) -> None:
        """Delete selected project."""
        table = self.query_one("#projects_table", DataTable)
        if table.cursor_row is not None:
            row = table.get_row_at(table.cursor_row)
            if row:
                project_name = row[0]
                confirmed = await self.app.push_screen_wait(
                    ConfirmDialog(
                        f"Delete project '{project_name}'?", "Confirm Delete"
                    )
                )
                if confirmed:
                    result = self.api_client.delete_project(project_name)
                    if "error" in result:
                        self.update_status(f"[red]Error: {result['error']}[/red]")
                    else:
                        self.update_status(f"[green]Deleted '{project_name}'[/green]")
                        self.action_refresh()
        else:
            self.update_status("[yellow]No project selected[/yellow]")

    def action_back(self) -> None:
        """Go back to home screen."""
        self.app.pop_screen()

    def update_status(self, message: str) -> None:
        """Update status message."""
        status = self.query_one("#project_status", Static)
        status.update(message)

    @on(Button.Pressed, "#btn_new")
    def handle_new(self) -> None:
        self.action_new_project()

    @on(Button.Pressed, "#btn_load")
    def handle_load(self) -> None:
        self.action_load_project()

    @on(Button.Pressed, "#btn_delete")
    def handle_delete(self) -> None:
        self.action_delete_project()

    @on(Button.Pressed, "#btn_refresh")
    def handle_refresh(self) -> None:
        self.action_refresh()


# ============================================================================
# Project Creation Screen
# ============================================================================


class ProjectCreateScreen(Screen):
    """Screen for creating new projects."""

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            yield Static("[bold]Create New Project[/bold]", id="create_title")
            yield Rule()
            yield Label("Project Name:")
            yield Input(placeholder="my-project", id="project_name")
            yield Label("Objective:")
            yield TextArea(id="project_objective")
            yield Label("Base Model:")
            yield Input(
                placeholder="unsloth/llama-2-7b-bnb-4bit", id="project_base_model"
            )
            yield Label("Dataset Format:")
            yield Select(
                [("ShareGPT", "sharegpt"), ("Alpaca", "alpaca")],
                value="sharegpt",
                id="project_format",
            )
            yield Label("AI Provider:")
            yield Select(
                [("Ollama", "ollama"), ("Anthropic", "anthropic"), ("OpenAI", "openai")],
                value="ollama",
                id="ai_provider",
            )
            yield Label("AI Model:")
            yield Input(placeholder="llama2", id="ai_model")
            yield Rule()
            yield Horizontal(
                Button("Create", variant="success", id="btn_create"),
                Button("Cancel", variant="default", id="btn_cancel"),
            )
            yield Static("", id="create_status")
        yield Footer()

    @on(Button.Pressed, "#btn_create")
    async def handle_create(self) -> None:
        """Create the project."""
        name = self.query_one("#project_name", Input).value
        objective = self.query_one("#project_objective", TextArea).text
        base_model = self.query_one("#project_base_model", Input).value
        dataset_format = self.query_one("#project_format", Select).value
        ai_provider = self.query_one("#ai_provider", Select).value
        ai_model = self.query_one("#ai_model", Input).value

        if not name or not objective:
            self.update_status("[red]Name and objective are required[/red]")
            return

        data = {
            "name": name,
            "objective": objective,
            "base_model": base_model or "unsloth/llama-2-7b-bnb-4bit",
            "dataset_format": dataset_format,
            "ai_config": {"provider": ai_provider, "model": ai_model or "llama2"},
        }

        result = self.api_client.create_project(data)
        if "error" in result:
            self.update_status(f"[red]Error: {result['error']}[/red]")
        else:
            await self.app.push_screen_wait(
                MessageDialog(
                    f"Project '{name}' created successfully!", "Success", "success"
                )
            )
            self.app.pop_screen()

    @on(Button.Pressed, "#btn_cancel")
    def handle_cancel(self) -> None:
        self.action_cancel()

    def action_save(self) -> None:
        """Save the project."""
        self.handle_create()

    def action_cancel(self) -> None:
        """Cancel and go back."""
        self.app.pop_screen()

    def update_status(self, message: str) -> None:
        """Update status message."""
        status = self.query_one("#create_status", Static)
        status.update(message)


# ============================================================================
# XML Editor Screen
# ============================================================================


class XMLEditorScreen(Screen):
    """Screen for editing XML patterns."""

    BINDINGS = [
        Binding("a", "add_tag", "Add Tag"),
        Binding("r", "remove_tag", "Remove Tag"),
        Binding("p", "preview", "Preview"),
        Binding("s", "save", "Save"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.current_project = None
        self.xml_patterns = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Static("[bold]XML Pattern Editor[/bold]", id="xml_title")
            yield Label("Project:")
            yield Input(placeholder="Enter project name", id="xml_project_name")
            yield Button("Load Project", variant="primary", id="btn_load_project")
            yield Rule()
            yield DataTable(id="xml_tags_table")
            yield Horizontal(
                Button("Add Tag", variant="success", id="btn_add_tag"),
                Button("Remove Tag", variant="error", id="btn_remove_tag"),
                Button("Preview", variant="default", id="btn_preview"),
                Button("Save", variant="primary", id="btn_save"),
            )
            yield Rule()
            yield Label("Pattern Preview:")
            with VerticalScroll(id="preview_scroll"):
                yield Static("", id="xml_preview")
            yield Static("", id="xml_status")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen."""
        table = self.query_one("#xml_tags_table", DataTable)
        table.add_columns("Tag Name", "Description", "Constraint Type", "Required")
        table.cursor_type = "row"

    @on(Button.Pressed, "#btn_load_project")
    def handle_load_project(self) -> None:
        """Load project for editing."""
        project_name = self.query_one("#xml_project_name", Input).value
        if not project_name:
            self.update_status("[yellow]Enter a project name[/yellow]")
            return

        result = self.api_client.get_project(project_name)
        if "error" in result:
            self.update_status(f"[red]Error: {result['error']}[/red]")
            return

        self.current_project = result
        self.xml_patterns = result.get("xml_patterns", [])
        self.refresh_tags_table()
        self.action_preview()
        self.update_status(f"[green]Loaded project '{project_name}'[/green]")

    def refresh_tags_table(self) -> None:
        """Refresh the tags table."""
        table = self.query_one("#xml_tags_table", DataTable)
        table.clear()

        for pattern in self.xml_patterns:
            table.add_row(
                pattern.get("tag_name", ""),
                pattern.get("description", "")[:40] + "..."
                if len(pattern.get("description", "")) > 40
                else pattern.get("description", ""),
                pattern.get("constraint_type", "free_form"),
                "Yes" if pattern.get("required", True) else "No",
            )

    def action_add_tag(self) -> None:
        """Add a new tag (simplified for demo)."""
        self.app.push_screen("xml_tag_editor")

    def action_remove_tag(self) -> None:
        """Remove selected tag."""
        table = self.query_one("#xml_tags_table", DataTable)
        if table.cursor_row is not None and self.xml_patterns:
            if table.cursor_row < len(self.xml_patterns):
                removed = self.xml_patterns.pop(table.cursor_row)
                self.refresh_tags_table()
                self.action_preview()
                self.update_status(
                    f"[yellow]Removed tag '{removed.get('tag_name', '')}'[/yellow]"
                )
        else:
            self.update_status("[yellow]No tag selected[/yellow]")

    def action_preview(self) -> None:
        """Preview the XML pattern."""
        if not self.xml_patterns:
            preview_text = "[dim]No XML patterns defined[/dim]"
        else:
            preview_lines = ["[cyan]<!-- XML Pattern Template -->[/cyan]", ""]
            for pattern in self.xml_patterns:
                tag_name = pattern.get("tag_name", "tag")
                description = pattern.get("description", "")
                preview_lines.append(f"[dim]<!-- {description} -->[/dim]")
                preview_lines.append(f"[green]<{tag_name}>[/green][yellow]...[/yellow][green]</{tag_name}>[/green]")
                preview_lines.append("")
            preview_text = "\n".join(preview_lines)

        preview = self.query_one("#xml_preview", Static)
        preview.update(preview_text)

    def action_save(self) -> None:
        """Save the XML patterns to the project."""
        if not self.current_project:
            self.update_status("[yellow]No project loaded[/yellow]")
            return

        project_name = self.current_project.get("name")
        data = {"xml_patterns": self.xml_patterns}

        result = self.api_client.update_project(project_name, data)
        if "error" in result:
            self.update_status(f"[red]Error: {result['error']}[/red]")
        else:
            self.update_status(f"[green]Saved patterns for '{project_name}'[/green]")

    def action_back(self) -> None:
        """Go back."""
        self.app.pop_screen()

    def update_status(self, message: str) -> None:
        """Update status message."""
        status = self.query_one("#xml_status", Static)
        status.update(message)

    @on(Button.Pressed, "#btn_add_tag")
    def handle_add_tag(self) -> None:
        self.action_add_tag()

    @on(Button.Pressed, "#btn_remove_tag")
    def handle_remove_tag(self) -> None:
        self.action_remove_tag()

    @on(Button.Pressed, "#btn_preview")
    def handle_preview(self) -> None:
        self.action_preview()

    @on(Button.Pressed, "#btn_save")
    def handle_save(self) -> None:
        self.action_save()


# ============================================================================
# XML Tag Editor Screen
# ============================================================================


class XMLTagEditorScreen(Screen):
    """Screen for editing individual XML tags."""

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            yield Static("[bold]Add XML Tag[/bold]")
            yield Rule()
            yield Label("Tag Name:")
            yield Input(placeholder="thinking", id="tag_name")
            yield Label("Description:")
            yield TextArea(id="tag_description")
            yield Label("Constraint Type:")
            yield Select(
                [
                    ("Free Form", "free_form"),
                    ("Regex", "regex"),
                    ("List", "list"),
                    ("Range", "range"),
                ],
                value="free_form",
                id="tag_constraint",
            )
            yield Label("Constraints (comma-separated for list):")
            yield Input(placeholder="value1,value2,value3", id="tag_constraints")
            yield Label("Required:")
            yield Select([("Yes", "true"), ("No", "false")], value="true", id="tag_required")
            yield Rule()
            yield Horizontal(
                Button("Save", variant="success", id="btn_save_tag"),
                Button("Cancel", variant="default", id="btn_cancel_tag"),
            )
            yield Static("", id="tag_status")
        yield Footer()

    @on(Button.Pressed, "#btn_save_tag")
    def handle_save_tag(self) -> None:
        """Save the tag."""
        tag_name = self.query_one("#tag_name", Input).value
        description = self.query_one("#tag_description", TextArea).text
        constraint_type = self.query_one("#tag_constraint", Select).value
        constraints = self.query_one("#tag_constraints", Input).value
        required = self.query_one("#tag_required", Select).value == "true"

        if not tag_name:
            self.update_status("[red]Tag name is required[/red]")
            return

        # Get the XML editor screen and add the tag
        xml_screen = None
        for screen in self.app.screen_stack:
            if isinstance(screen, XMLEditorScreen):
                xml_screen = screen
                break

        if xml_screen:
            new_tag = {
                "tag_name": tag_name,
                "description": description,
                "constraint_type": constraint_type,
                "required": required,
            }

            if constraints:
                if constraint_type == "list":
                    new_tag["values"] = [v.strip() for v in constraints.split(",")]
                else:
                    new_tag["constraints"] = constraints

            xml_screen.xml_patterns.append(new_tag)
            xml_screen.refresh_tags_table()
            xml_screen.action_preview()

        self.app.pop_screen()

    @on(Button.Pressed, "#btn_cancel_tag")
    def handle_cancel_tag(self) -> None:
        self.action_cancel()

    def action_save(self) -> None:
        """Save the tag."""
        self.handle_save_tag()

    def action_cancel(self) -> None:
        """Cancel and go back."""
        self.app.pop_screen()

    def update_status(self, message: str) -> None:
        """Update status message."""
        status = self.query_one("#tag_status", Static)
        status.update(message)


# ============================================================================
# Generation Screen
# ============================================================================


class GenerationScreen(Screen):
    """Screen for configuring and starting data generation."""

    BINDINGS = [
        Binding("g", "generate", "Generate"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Static("[bold]Synthetic Data Generation[/bold]", id="gen_title")
            yield Rule()
            yield Label("Project Name:")
            yield Input(placeholder="my-project", id="gen_project_name")
            yield Label("Number of Examples:")
            yield Input(placeholder="100", id="gen_num_examples")
            yield Label("Temperature (0.0-2.0):")
            yield Input(placeholder="0.7", id="gen_temperature")
            yield Label("Batch Size:")
            yield Input(placeholder="10", id="gen_batch_size")
            yield Rule()
            yield Button("Generate Dataset", variant="success", id="btn_generate")
            yield ProgressBar(total=100, show_eta=True, id="gen_progress")
            yield Rule()
            yield Label("Generation Log:")
            yield Log(id="gen_log", auto_scroll=True)
            yield Static("", id="gen_status")
        yield Footer()

    @on(Button.Pressed, "#btn_generate")
    async def handle_generate(self) -> None:
        """Start dataset generation."""
        project_name = self.query_one("#gen_project_name", Input).value
        num_examples_str = self.query_one("#gen_num_examples", Input).value
        temperature_str = self.query_one("#gen_temperature", Input).value
        batch_size_str = self.query_one("#gen_batch_size", Input).value

        if not project_name:
            self.update_status("[red]Project name is required[/red]")
            return

        try:
            num_examples = int(num_examples_str) if num_examples_str else 100
            temperature = float(temperature_str) if temperature_str else None
            batch_size = int(batch_size_str) if batch_size_str else 10
        except ValueError:
            self.update_status("[red]Invalid numeric value[/red]")
            return

        data = {
            "project_name": project_name,
            "num_examples": num_examples,
            "batch_size": batch_size,
        }
        if temperature is not None:
            data["temperature"] = temperature

        log = self.query_one("#gen_log", Log)
        progress = self.query_one("#gen_progress", ProgressBar)

        log.clear()
        log.write_line(f"[cyan]Starting generation for project: {project_name}[/cyan]")
        log.write_line(f"[cyan]Generating {num_examples} examples...[/cyan]")

        # Simulate progress (in real implementation, this would track actual progress)
        progress.update(total=num_examples, progress=0)

        result = self.api_client.generate_dataset(data)

        if "error" in result:
            log.write_line(f"[red]Error: {result['error']}[/red]")
            self.update_status(f"[red]Generation failed[/red]")
        else:
            progress.update(progress=num_examples)
            log.write_line(f"[green]Successfully generated dataset![/green]")
            log.write_line(f"[green]Filename: {result.get('dataset_filename', 'N/A')}[/green]")
            log.write_line(f"[green]Generated: {result.get('num_generated', 0)} examples[/green]")
            self.update_status("[green]Generation complete![/green]")

            await self.app.push_screen_wait(
                MessageDialog("Dataset generated successfully!", "Success", "success")
            )

    def action_generate(self) -> None:
        """Generate dataset."""
        self.handle_generate()

    def action_back(self) -> None:
        """Go back."""
        self.app.pop_screen()

    def update_status(self, message: str) -> None:
        """Update status message."""
        status = self.query_one("#gen_status", Static)
        status.update(message)


# ============================================================================
# Training Screen
# ============================================================================


class TrainingScreen(Screen):
    """Screen for configuring and monitoring training."""

    BINDINGS = [
        Binding("t", "train", "Train"),
        Binding("s", "status", "Status"),
        Binding("c", "cancel", "Cancel"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.current_job_id = None
        self.update_timer = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Static("[bold]Model Training[/bold]", id="train_title")
            yield Rule()
            with Horizontal():
                with Vertical():
                    yield Label("Project Name:")
                    yield Input(placeholder="my-project", id="train_project_name")
                    yield Label("Dataset Filename:")
                    yield Input(placeholder="dataset_20231101.jsonl", id="train_dataset")
                    yield Label("Output Directory (optional):")
                    yield Input(placeholder="models/my-model", id="train_output_dir")
                    yield Rule()
                    yield Horizontal(
                        Button("Start Training", variant="success", id="btn_train"),
                        Button("Check Status", variant="primary", id="btn_status"),
                        Button("Cancel Job", variant="error", id="btn_cancel"),
                    )
                with Vertical():
                    yield Label("Training Status:")
                    yield Static("Not started", id="train_status_text")
                    yield Label("Progress:")
                    yield ProgressBar(total=100, show_eta=True, id="train_progress")
                    yield Label("Current Loss:")
                    yield Static("N/A", id="train_loss")
                    yield Label("Epoch / Step:")
                    yield Static("N/A", id="train_epoch_step")
            yield Rule()
            yield Label("Training Log:")
            yield Log(id="train_log", auto_scroll=True)
            yield Static("", id="train_status")
        yield Footer()

    @on(Button.Pressed, "#btn_train")
    async def handle_train(self) -> None:
        """Start training."""
        project_name = self.query_one("#train_project_name", Input).value
        dataset_filename = self.query_one("#train_dataset", Input).value
        output_dir = self.query_one("#train_output_dir", Input).value

        if not project_name or not dataset_filename:
            self.update_status("[red]Project name and dataset are required[/red]")
            return

        data = {
            "project_name": project_name,
            "dataset_filename": dataset_filename,
        }
        if output_dir:
            data["output_dir"] = output_dir

        log = self.query_one("#train_log", Log)
        log.clear()
        log.write_line(f"[cyan]Starting training for project: {project_name}[/cyan]")
        log.write_line(f"[cyan]Using dataset: {dataset_filename}[/cyan]")

        result = self.api_client.start_training(data)

        if "error" in result:
            log.write_line(f"[red]Error: {result['error']}[/red]")
            self.update_status(f"[red]Training failed to start[/red]")
        else:
            self.current_job_id = result.get("job_id")
            log.write_line(f"[green]Training job started![/green]")
            log.write_line(f"[green]Job ID: {self.current_job_id}[/green]")
            self.update_status("[green]Training started![/green]")

            # Start auto-refresh
            self.start_auto_refresh()

    @on(Button.Pressed, "#btn_status")
    def handle_status(self) -> None:
        """Check training status."""
        self.action_status()

    @on(Button.Pressed, "#btn_cancel")
    async def handle_cancel_job(self) -> None:
        """Cancel training job."""
        if not self.current_job_id:
            self.update_status("[yellow]No active job[/yellow]")
            return

        confirmed = await self.app.push_screen_wait(
            ConfirmDialog(f"Cancel training job '{self.current_job_id}'?", "Confirm Cancel")
        )

        if confirmed:
            result = self.api_client.cancel_training(self.current_job_id)
            if "error" in result:
                self.update_status(f"[red]Error: {result['error']}[/red]")
            else:
                log = self.query_one("#train_log", Log)
                log.write_line(f"[yellow]Training job cancelled[/yellow]")
                self.update_status("[yellow]Job cancelled[/yellow]")
                self.stop_auto_refresh()

    def action_train(self) -> None:
        """Start training."""
        self.handle_train()

    def action_status(self) -> None:
        """Check training status."""
        if not self.current_job_id:
            self.update_status("[yellow]No active job[/yellow]")
            return

        result = self.api_client.get_training_status(self.current_job_id)

        if "error" in result:
            self.update_status(f"[red]Error: {result['error']}[/red]")
            return

        # Update UI with status
        status_text = self.query_one("#train_status_text", Static)
        status_text.update(f"[cyan]{result.get('status', 'unknown').upper()}[/cyan]")

        progress = self.query_one("#train_progress", ProgressBar)
        total_steps = result.get("total_steps", 100)
        current_step = result.get("current_step", 0)
        if total_steps:
            progress.update(total=total_steps, progress=current_step)

        loss = self.query_one("#train_loss", Static)
        loss_value = result.get("loss")
        if loss_value is not None:
            loss.update(f"[yellow]{loss_value:.4f}[/yellow]")

        epoch_step = self.query_one("#train_epoch_step", Static)
        epoch_text = f"Epoch: {result.get('current_epoch', 0)}/{result.get('total_epochs', 0)} | "
        epoch_text += f"Step: {current_step}/{total_steps}"
        epoch_step.update(epoch_text)

        log = self.query_one("#train_log", Log)
        if result.get("status") == "completed":
            log.write_line("[green]Training completed![/green]")
            self.stop_auto_refresh()
        elif result.get("status") == "failed":
            error_msg = result.get("error_message", "Unknown error")
            log.write_line(f"[red]Training failed: {error_msg}[/red]")
            self.stop_auto_refresh()

    def start_auto_refresh(self) -> None:
        """Start auto-refresh timer."""
        if self.update_timer:
            self.update_timer.cancel()
        self.update_timer = self.set_interval(5.0, self.action_status)

    def stop_auto_refresh(self) -> None:
        """Stop auto-refresh timer."""
        if self.update_timer:
            self.update_timer.cancel()
            self.update_timer = None

    def action_cancel(self) -> None:
        """Cancel training."""
        self.handle_cancel_job()

    def action_back(self) -> None:
        """Go back."""
        self.stop_auto_refresh()
        self.app.pop_screen()

    def update_status(self, message: str) -> None:
        """Update status message."""
        status = self.query_one("#train_status", Static)
        status.update(message)


# ============================================================================
# Export Screen
# ============================================================================


class ExportScreen(Screen):
    """Screen for exporting trained models."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Static("[bold]Model Export[/bold]", id="export_title")
            yield Rule()
            yield Label("Select Model Directory:")
            yield Input(placeholder="models/my-project", id="export_model_dir")
            yield Label("Export Format:")
            yield Select(
                [
                    ("GGUF", "gguf"),
                    ("PyTorch", "pytorch"),
                    ("HuggingFace", "huggingface"),
                ],
                value="gguf",
                id="export_format",
            )
            yield Label("Quantization:")
            yield Select(
                [
                    ("4-bit", "4bit"),
                    ("8-bit", "8bit"),
                    ("16-bit", "16bit"),
                    ("None", "none"),
                ],
                value="4bit",
                id="export_quant",
            )
            yield Rule()
            yield Button("Export Model", variant="success", id="btn_export")
            yield Rule()
            yield Label("Export Log:")
            yield Log(id="export_log", auto_scroll=True)
            yield Static("", id="export_status")
        yield Footer()

    @on(Button.Pressed, "#btn_export")
    def handle_export(self) -> None:
        """Export the model."""
        model_dir = self.query_one("#export_model_dir", Input).value
        export_format = self.query_one("#export_format", Select).value
        quantization = self.query_one("#export_quant", Select).value

        if not model_dir:
            self.update_status("[red]Model directory is required[/red]")
            return

        log = self.query_one("#export_log", Log)
        log.clear()
        log.write_line(f"[cyan]Exporting model from: {model_dir}[/cyan]")
        log.write_line(f"[cyan]Format: {export_format}[/cyan]")
        log.write_line(f"[cyan]Quantization: {quantization}[/cyan]")
        log.write_line("[yellow]Export functionality coming soon...[/yellow]")
        self.update_status("[yellow]Export feature not yet implemented[/yellow]")

    def action_back(self) -> None:
        """Go back."""
        self.app.pop_screen()

    def update_status(self, message: str) -> None:
        """Update status message."""
        status = self.query_one("#export_status", Static)
        status.update(message)


# ============================================================================
# Main Application
# ============================================================================


class ModelTrainTUI(App):
    """Main TUI application for model training."""

    CSS = """
    Screen {
        background: $surface;
    }

    Container {
        height: 100%;
        padding: 1;
    }

    #welcome {
        width: 100%;
        height: 100%;
        content-align: center middle;
        padding: 2;
    }

    DataTable {
        height: auto;
        max-height: 20;
        margin: 1 0;
    }

    Input {
        margin: 0 0 1 0;
    }

    TextArea {
        height: 5;
        margin: 0 0 1 0;
    }

    Select {
        margin: 0 0 1 0;
    }

    Button {
        margin: 0 1;
    }

    Horizontal {
        height: auto;
        margin: 1 0;
    }

    ProgressBar {
        margin: 1 0;
    }

    Log {
        height: 15;
        border: solid $primary;
        margin: 1 0;
    }

    #project_title, #xml_title, #gen_title, #train_title, #export_title, #create_title {
        margin: 0 0 1 0;
        text-style: bold;
    }

    #project_status, #xml_status, #gen_status, #train_status, #create_status, #export_status, #tag_status {
        margin: 1 0 0 0;
        padding: 1;
        background: $panel;
    }

    Rule {
        margin: 1 0;
    }

    Label {
        margin: 1 0 0 0;
    }

    VerticalScroll {
        height: 100%;
    }

    #preview_scroll {
        height: 10;
        border: solid $primary;
        margin: 1 0;
    }

    #xml_preview {
        padding: 1;
    }

    Vertical {
        width: 1fr;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("h", "home", "Home", show=True),
    ]

    SCREENS = {
        "home": HomeScreen,
        "projects": ProjectScreen,
        "project_create": ProjectCreateScreen,
        "xml_editor": XMLEditorScreen,
        "xml_tag_editor": XMLTagEditorScreen,
        "generation": GenerationScreen,
        "training": TrainingScreen,
        "export": ExportScreen,
    }

    def on_mount(self) -> None:
        """Initialize the application."""
        self.title = "Model Training TUI"
        self.sub_title = "Synthetic Data & Fine-Tuning Platform"
        self.push_screen("home")

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_home(self) -> None:
        """Go to home screen."""
        # Pop all screens except home
        while len(self.screen_stack) > 1:
            self.pop_screen()


# ============================================================================
# Entry Point
# ============================================================================


def main():
    """Run the TUI application."""
    app = ModelTrainTUI()
    app.run()


if __name__ == "__main__":
    main()
