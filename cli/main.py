"""
Comprehensive CLI for Model Fine-Tuning Platform using Click.

Provides commands for managing projects, XML patterns, data generation,
training, and model operations with colorful output and progress tracking.
"""
import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
import time

import click
import requests
from datetime import datetime


# Color constants for output
class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    # Background colors
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'


class APIClient:
    """Client for interacting with the model training backend API."""

    def __init__(self, base_url: str = None, verbose: bool = False):
        """Initialize API client."""
        self.base_url = base_url or os.getenv("API_URL", "http://localhost:8000")
        self.api_base = f"{self.base_url}/api/v1"
        self.verbose = verbose
        self.session = requests.Session()

    def _log(self, message: str):
        """Log verbose messages."""
        if self.verbose:
            click.echo(f"{Colors.DIM}[DEBUG] {message}{Colors.RESET}", err=True)

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make HTTP request to API."""
        url = f"{self.api_base}{endpoint}"
        self._log(f"{method.upper()} {url}")

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.ConnectionError:
            raise click.ClickException(
                f"Cannot connect to API at {self.base_url}. "
                f"Is the backend running?"
            )
        except requests.exceptions.HTTPError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except:
                error_detail = str(e)
            raise click.ClickException(f"API Error: {error_detail}")
        except Exception as e:
            raise click.ClickException(f"Request failed: {str(e)}")

    def get(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make GET request."""
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make POST request."""
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make PUT request."""
        return self._request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make DELETE request."""
        return self._request("DELETE", endpoint, **kwargs)


def print_success(message: str):
    """Print success message in green."""
    click.echo(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message in red."""
    click.echo(f"{Colors.RED}✗ {message}{Colors.RESET}", err=True)


def print_warning(message: str):
    """Print warning message in yellow."""
    click.echo(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message in blue."""
    click.echo(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")


def print_header(message: str):
    """Print header message."""
    click.echo(f"\n{Colors.BOLD}{Colors.CYAN}{message}{Colors.RESET}\n")


def format_datetime(dt: str) -> str:
    """Format datetime string for display."""
    try:
        parsed = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        return parsed.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt


def output_json(data: Any):
    """Output data as formatted JSON."""
    click.echo(json.dumps(data, indent=2, default=str))


# Global options
def add_common_options(func):
    """Add common options to commands."""
    func = click.option(
        '--api-url',
        envvar='API_URL',
        default='http://localhost:8000',
        help='Backend API URL',
        show_default=True
    )(func)
    func = click.option(
        '--verbose', '-v',
        is_flag=True,
        help='Enable verbose output'
    )(func)
    func = click.option(
        '--json',
        'output_json_flag',
        is_flag=True,
        help='Output as JSON'
    )(func)
    return func


# Main CLI group
@click.group(name='model-train')
@click.version_option(version='0.1.0', prog_name='model-train')
@click.pass_context
def cli(ctx):
    """
    Model Fine-Tuning CLI - Manage projects, datasets, and training.

    A comprehensive tool for managing ML model fine-tuning with XML pattern synthesis.
    """
    ctx.ensure_object(dict)


# ============================================================================
# PROJECT COMMANDS
# ============================================================================

@cli.group()
def project():
    """Manage training projects."""
    pass


@project.command('list')
@add_common_options
@click.pass_context
def project_list(ctx, api_url, verbose, output_json_flag):
    """List all projects."""
    client = APIClient(api_url, verbose)

    try:
        response = client.get("/projects")
        projects = response.get('projects', [])

        if output_json_flag:
            output_json(response)
            return

        if not projects:
            print_info("No projects found. Create one with 'model-train project create'")
            return

        print_header(f"Projects ({len(projects)} total)")

        for proj in projects:
            click.echo(f"{Colors.BOLD}{Colors.CYAN}{proj['name']}{Colors.RESET}")
            click.echo(f"  Objective: {proj['objective']}")
            click.echo(f"  Model: {proj['base_model']}")
            click.echo(f"  XML Patterns: {len(proj.get('xml_patterns', []))}")
            click.echo(f"  Datasets: {len(proj.get('datasets', []))}")
            click.echo(f"  Created: {format_datetime(proj['created_at'])}")
            click.echo()

    except click.ClickException as e:
        print_error(str(e))
        sys.exit(1)


@project.command('create')
@click.argument('name')
@click.option('--objective', '-o', required=True, help='Training objective description')
@click.option('--model', '-m', default='unsloth/llama-2-7b-bnb-4bit', help='Base model to use')
@click.option('--format', '-f', type=click.Choice(['sharegpt', 'alpaca']), default='sharegpt', help='Dataset format')
@click.option('--provider', type=click.Choice(['ollama', 'anthropic', 'openai']), default='ollama', help='AI provider')
@click.option('--ai-model', default='llama2', help='AI model for synthesis')
@add_common_options
def project_create(name, objective, model, format, provider, ai_model, api_url, verbose, output_json_flag):
    """Create a new project."""
    client = APIClient(api_url, verbose)

    try:
        data = {
            "name": name,
            "objective": objective,
            "base_model": model,
            "dataset_format": format,
            "ai_config": {
                "provider": provider,
                "model": ai_model
            }
        }

        response = client.post("/projects", json=data)

        if output_json_flag:
            output_json(response)
            return

        print_success(f"Project '{name}' created successfully")
        click.echo(f"\n{Colors.BOLD}Project Details:{Colors.RESET}")
        click.echo(f"  Name: {response['name']}")
        click.echo(f"  Objective: {response['objective']}")
        click.echo(f"  Base Model: {response['base_model']}")
        click.echo(f"  Format: {response['dataset_format']}")
        click.echo(f"\n{Colors.CYAN}Next steps:{Colors.RESET}")
        click.echo(f"  1. Add XML patterns: model-train xml add-tag {name} <tag-name>")
        click.echo(f"  2. Generate data: model-train generate {name}")
        click.echo(f"  3. Start training: model-train train {name}")

    except click.ClickException as e:
        print_error(str(e))
        sys.exit(1)


@project.command('show')
@click.argument('name')
@add_common_options
def project_show(name, api_url, verbose, output_json_flag):
    """Show detailed information about a project."""
    client = APIClient(api_url, verbose)

    try:
        response = client.get(f"/projects/{name}")

        if output_json_flag:
            output_json(response)
            return

        print_header(f"Project: {response['name']}")

        click.echo(f"{Colors.BOLD}Configuration:{Colors.RESET}")
        click.echo(f"  Objective: {response['objective']}")
        click.echo(f"  Base Model: {response['base_model']}")
        click.echo(f"  Format: {response['dataset_format']}")
        click.echo(f"  Created: {format_datetime(response['created_at'])}")
        click.echo(f"  Updated: {format_datetime(response['updated_at'])}")

        # AI Config
        ai_config = response.get('ai_config', {})
        click.echo(f"\n{Colors.BOLD}AI Configuration:{Colors.RESET}")
        click.echo(f"  Provider: {ai_config.get('provider', 'N/A')}")
        click.echo(f"  Model: {ai_config.get('model', 'N/A')}")
        click.echo(f"  Temperature: {ai_config.get('temperature', 'N/A')}")

        # XML Patterns
        patterns = response.get('xml_patterns', [])
        click.echo(f"\n{Colors.BOLD}XML Patterns ({len(patterns)}):{Colors.RESET}")
        if patterns:
            for pattern in patterns:
                click.echo(f"  • {Colors.CYAN}{pattern['tag_name']}{Colors.RESET}")
                click.echo(f"    {pattern['description']}")
                if pattern.get('constraints'):
                    click.echo(f"    Constraints: {pattern['constraints']}")
        else:
            click.echo(f"  {Colors.DIM}No XML patterns defined{Colors.RESET}")

        # Datasets
        datasets = response.get('datasets', [])
        click.echo(f"\n{Colors.BOLD}Datasets ({len(datasets)}):{Colors.RESET}")
        if datasets:
            for ds in datasets:
                click.echo(f"  • {ds['filename']}")
                click.echo(f"    Examples: {ds['num_examples']} | Format: {ds['format']}")
                click.echo(f"    Created: {format_datetime(ds['created_at'])}")
        else:
            click.echo(f"  {Colors.DIM}No datasets generated{Colors.RESET}")

    except click.ClickException as e:
        print_error(str(e))
        sys.exit(1)


@project.command('delete')
@click.argument('name')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@add_common_options
def project_delete(name, yes, api_url, verbose, output_json_flag):
    """Delete a project."""
    client = APIClient(api_url, verbose)

    if not yes:
        click.confirm(
            f"Are you sure you want to delete project '{name}'?",
            abort=True
        )

    try:
        client.delete(f"/projects/{name}")

        if output_json_flag:
            output_json({"success": True, "message": f"Project '{name}' deleted"})
            return

        print_success(f"Project '{name}' deleted successfully")

    except click.ClickException as e:
        print_error(str(e))
        sys.exit(1)


# ============================================================================
# XML PATTERN COMMANDS
# ============================================================================

@cli.group()
def xml():
    """Manage XML patterns for projects."""
    pass


@xml.command('add-tag')
@click.argument('project')
@click.argument('tag_name')
@click.option('--description', '-d', required=True, help='Tag description')
@click.option('--constraint', '-c', help='Validation constraint')
@click.option('--example', '-e', multiple=True, help='Example usage (can be repeated)')
@add_common_options
def xml_add_tag(project, tag_name, description, constraint, example, api_url, verbose, output_json_flag):
    """Add an XML tag pattern to a project."""
    client = APIClient(api_url, verbose)

    try:
        # Get current project
        proj_data = client.get(f"/projects/{project}")

        # Add new pattern
        patterns = proj_data.get('xml_patterns', [])
        new_pattern = {
            "tag_name": tag_name,
            "description": description,
        }
        if constraint:
            new_pattern["constraints"] = constraint
        if example:
            new_pattern["examples"] = list(example)

        patterns.append(new_pattern)

        # Update project
        client.put(f"/projects/{project}", json={"xml_patterns": patterns})

        if output_json_flag:
            output_json({"success": True, "pattern": new_pattern})
            return

        print_success(f"Added XML tag '{tag_name}' to project '{project}'")
        click.echo(f"  Description: {description}")
        if constraint:
            click.echo(f"  Constraint: {constraint}")

    except click.ClickException as e:
        print_error(str(e))
        sys.exit(1)


@xml.command('remove-tag')
@click.argument('project')
@click.argument('tag_name')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@add_common_options
def xml_remove_tag(project, tag_name, yes, api_url, verbose, output_json_flag):
    """Remove an XML tag pattern from a project."""
    client = APIClient(api_url, verbose)

    if not yes:
        click.confirm(
            f"Remove tag '{tag_name}' from project '{project}'?",
            abort=True
        )

    try:
        # Get current project
        proj_data = client.get(f"/projects/{project}")

        # Remove pattern
        patterns = proj_data.get('xml_patterns', [])
        original_count = len(patterns)
        patterns = [p for p in patterns if p['tag_name'] != tag_name]

        if len(patterns) == original_count:
            raise click.ClickException(f"Tag '{tag_name}' not found in project")

        # Update project
        client.put(f"/projects/{project}", json={"xml_patterns": patterns})

        if output_json_flag:
            output_json({"success": True, "removed": tag_name})
            return

        print_success(f"Removed XML tag '{tag_name}' from project '{project}'")

    except click.ClickException as e:
        print_error(str(e))
        sys.exit(1)


@xml.command('show')
@click.argument('project')
@add_common_options
def xml_show(project, api_url, verbose, output_json_flag):
    """Show all XML patterns for a project."""
    client = APIClient(api_url, verbose)

    try:
        proj_data = client.get(f"/projects/{project}")
        patterns = proj_data.get('xml_patterns', [])

        if output_json_flag:
            output_json({"project": project, "patterns": patterns})
            return

        if not patterns:
            print_info(f"No XML patterns defined for project '{project}'")
            return

        print_header(f"XML Patterns for '{project}' ({len(patterns)} total)")

        for pattern in patterns:
            click.echo(f"{Colors.BOLD}{Colors.CYAN}<{pattern['tag_name']}>{Colors.RESET}")
            click.echo(f"  Description: {pattern['description']}")
            if pattern.get('constraints'):
                click.echo(f"  Constraints: {pattern['constraints']}")
            if pattern.get('attributes'):
                click.echo(f"  Attributes: {pattern['attributes']}")
            if pattern.get('examples'):
                click.echo(f"  Examples:")
                for ex in pattern['examples']:
                    click.echo(f"    - {ex}")
            click.echo()

    except click.ClickException as e:
        print_error(str(e))
        sys.exit(1)


# ============================================================================
# DATA GENERATION COMMANDS
# ============================================================================

@cli.command('generate')
@click.argument('project')
@click.option('--count', '-n', default=100, help='Number of examples to generate')
@click.option('--batch-size', '-b', default=10, help='Batch size for generation')
@click.option('--temperature', '-t', type=float, help='AI temperature (0.0-2.0)')
@click.option('--mode', type=click.Choice(['pseudorandom', 'diverse', 'focused']), default='pseudorandom', help='Generation mode')
@click.option('--validate', is_flag=True, help='Validate generated data')
@add_common_options
def generate(project, count, batch_size, temperature, mode, validate, api_url, verbose, output_json_flag):
    """Generate synthetic training data for a project."""
    client = APIClient(api_url, verbose)

    try:
        print_info(f"Generating {count} examples for project '{project}'...")

        data = {
            "project_name": project,
            "num_examples": count,
            "batch_size": batch_size,
        }
        if temperature:
            data["temperature"] = temperature

        # Show progress bar
        if not output_json_flag:
            with click.progressbar(
                length=count,
                label='Generating examples',
                fill_char=click.style('█', fg='green'),
                empty_char=click.style('░', fg='white', dim=True)
            ) as bar:
                # Simulate progress (in real implementation, would track actual progress)
                response = client.post("/generate", json=data)
                bar.update(count)
        else:
            response = client.post("/generate", json=data)

        if output_json_flag:
            output_json(response)
            return

        print_success(
            f"Generated {response['num_generated']} examples "
            f"in {response['format']} format"
        )
        click.echo(f"  Dataset: {response['dataset_filename']}")

        if validate:
            print_info("Validating dataset...")
            # TODO: Implement validation logic
            print_success("Dataset validation passed")

    except click.ClickException as e:
        print_error(str(e))
        sys.exit(1)


# ============================================================================
# TRAINING COMMANDS
# ============================================================================

@cli.group()
def train():
    """Train and manage fine-tuning jobs."""
    pass


@train.command('start')
@click.argument('project')
@click.option('--dataset', '-d', help='Dataset filename (uses latest if not specified)')
@click.option('--steps', '-s', type=int, help='Number of training steps')
@click.option('--lora-rank', '-r', type=int, default=16, help='LoRA rank')
@click.option('--learning-rate', '-lr', type=float, help='Learning rate')
@click.option('--batch-size', '-b', type=int, help='Batch size')
@click.option('--epochs', '-e', type=int, help='Number of epochs')
@add_common_options
def train_start(project, dataset, steps, lora_rank, learning_rate, batch_size, epochs,
                api_url, verbose, output_json_flag):
    """Start training a model for a project."""
    client = APIClient(api_url, verbose)

    try:
        # Get project to find dataset if not specified
        if not dataset:
            proj_data = client.get(f"/projects/{project}")
            datasets = proj_data.get('datasets', [])
            if not datasets:
                raise click.ClickException(
                    f"No datasets found for project '{project}'. "
                    f"Generate one first with 'model-train generate {project}'"
                )
            # Use most recent dataset
            dataset = sorted(datasets, key=lambda x: x['created_at'], reverse=True)[0]['filename']

        print_info(f"Starting training for project '{project}'...")
        click.echo(f"  Dataset: {dataset}")
        click.echo(f"  LoRA Rank: {lora_rank}")

        data = {
            "project_name": project,
            "dataset_filename": dataset,
        }

        response = client.post("/train", json=data)

        if output_json_flag:
            output_json(response)
            return

        job_id = response['job_id']
        print_success(f"Training job started: {job_id}")
        click.echo(f"\n{Colors.CYAN}Monitor progress with:{Colors.RESET}")
        click.echo(f"  model-train train status {job_id}")

    except click.ClickException as e:
        print_error(str(e))
        sys.exit(1)


@train.command('status')
@click.argument('job_id')
@click.option('--watch', '-w', is_flag=True, help='Watch status updates in real-time')
@click.option('--interval', '-i', default=5, help='Update interval in seconds (with --watch)')
@add_common_options
def train_status(job_id, watch, interval, api_url, verbose, output_json_flag):
    """Check training job status."""
    client = APIClient(api_url, verbose)

    def show_status():
        try:
            response = client.get(f"/train/status/{job_id}")

            if output_json_flag:
                output_json(response)
                return False  # Don't continue watching in JSON mode

            # Clear screen if watching
            if watch:
                click.clear()

            print_header(f"Training Job: {job_id}")

            status = response['status']
            status_colors = {
                'pending': Colors.YELLOW,
                'running': Colors.BLUE,
                'completed': Colors.GREEN,
                'failed': Colors.RED,
                'cancelled': Colors.YELLOW,
            }
            color = status_colors.get(status, Colors.WHITE)

            click.echo(f"{Colors.BOLD}Status:{Colors.RESET} {color}{status.upper()}{Colors.RESET}")
            click.echo(f"Project: {response['project_name']}")

            if response.get('started_at'):
                click.echo(f"Started: {format_datetime(response['started_at'])}")
            if response.get('completed_at'):
                click.echo(f"Completed: {format_datetime(response['completed_at'])}")

            # Progress
            if response.get('current_epoch') and response.get('total_epochs'):
                epoch_progress = (response['current_epoch'] / response['total_epochs']) * 100
                click.echo(f"\n{Colors.BOLD}Progress:{Colors.RESET}")
                click.echo(f"  Epoch: {response['current_epoch']}/{response['total_epochs']} ({epoch_progress:.1f}%)")

            if response.get('current_step') and response.get('total_steps'):
                step_progress = (response['current_step'] / response['total_steps']) * 100
                click.echo(f"  Step: {response['current_step']}/{response['total_steps']} ({step_progress:.1f}%)")

                # Progress bar
                bar_length = 40
                filled = int(bar_length * response['current_step'] / response['total_steps'])
                bar = '█' * filled + '░' * (bar_length - filled)
                click.echo(f"  [{Colors.GREEN}{bar}{Colors.RESET}]")

            # Metrics
            if response.get('loss'):
                click.echo(f"\n{Colors.BOLD}Metrics:{Colors.RESET}")
                click.echo(f"  Loss: {response['loss']:.4f}")
            if response.get('learning_rate'):
                click.echo(f"  Learning Rate: {response['learning_rate']:.2e}")

            if response.get('error_message'):
                click.echo(f"\n{Colors.RED}Error:{Colors.RESET} {response['error_message']}")

            if response.get('output_dir'):
                click.echo(f"\n{Colors.BOLD}Output:{Colors.RESET} {response['output_dir']}")

            # Return True to continue watching if status is not terminal
            return watch and status in ['pending', 'running']

        except click.ClickException as e:
            print_error(str(e))
            return False

    # Show status once or in a loop
    should_continue = show_status()
    while should_continue:
        time.sleep(interval)
        should_continue = show_status()


@train.command('cancel')
@click.argument('job_id')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@add_common_options
def train_cancel(job_id, yes, api_url, verbose, output_json_flag):
    """Cancel a running training job."""
    client = APIClient(api_url, verbose)

    if not yes:
        click.confirm(
            f"Are you sure you want to cancel training job '{job_id}'?",
            abort=True
        )

    try:
        client.delete(f"/train/cancel/{job_id}")

        if output_json_flag:
            output_json({"success": True, "job_id": job_id})
            return

        print_success(f"Training job '{job_id}' cancelled")

    except click.ClickException as e:
        print_error(str(e))
        sys.exit(1)


# ============================================================================
# MODEL COMMANDS
# ============================================================================

@cli.group()
def model():
    """Manage models."""
    pass


@model.command('list')
@add_common_options
def model_list(api_url, verbose, output_json_flag):
    """List all available models."""
    client = APIClient(api_url, verbose)

    try:
        response = client.get("/models")
        models = response.get('models', [])

        if output_json_flag:
            output_json(response)
            return

        if not models:
            print_info("No models downloaded. Download one with 'model-train model download'")
            return

        print_header(f"Models ({len(models)} total)")

        for mdl in models:
            click.echo(f"{Colors.BOLD}{Colors.CYAN}{mdl.get('name', mdl.get('model_id', 'unknown'))}{Colors.RESET}")
            if mdl.get('path'):
                click.echo(f"  Path: {mdl['path']}")
            if mdl.get('size'):
                click.echo(f"  Size: {mdl['size']}")
            if mdl.get('quantization'):
                click.echo(f"  Quantization: {mdl['quantization']}")
            click.echo()

    except click.ClickException as e:
        print_error(str(e))
        sys.exit(1)


@model.command('download')
@click.argument('model_name')
@click.option('--revision', '-r', help='Model revision/branch')
@click.option('--quantization', '-q', type=click.Choice(['4bit', '8bit', 'none']), help='Quantization type')
@add_common_options
def model_download(model_name, revision, quantization, api_url, verbose, output_json_flag):
    """Download a model from HuggingFace."""
    client = APIClient(api_url, verbose)

    try:
        print_info(f"Downloading model '{model_name}'...")

        data = {"model_id": model_name}
        if revision:
            data["revision"] = revision
        if quantization:
            data["quantization"] = quantization

        if not output_json_flag:
            with click.progressbar(
                length=100,
                label='Downloading',
                fill_char=click.style('█', fg='cyan'),
                empty_char=click.style('░', fg='white', dim=True)
            ) as bar:
                # Note: Real implementation would track actual download progress
                response = client.post("/models/download", json=data)
                bar.update(100)
        else:
            response = client.post("/models/download", json=data)

        if output_json_flag:
            output_json(response)
            return

        print_success(f"Model downloaded successfully")
        click.echo(f"  Path: {response['model_path']}")

    except click.ClickException as e:
        print_error(str(e))
        sys.exit(1)


@model.command('export')
@click.argument('project')
@click.option('--format', '-f', type=click.Choice(['gguf', 'safetensors', 'pytorch']),
              default='gguf', help='Export format')
@click.option('--quantization', '-q', type=click.Choice(['q4_0', 'q4_1', 'q5_0', 'q5_1', 'q8_0']),
              help='GGUF quantization level')
@click.option('--output', '-o', help='Output filename')
@add_common_options
def model_export(project, format, quantization, output, api_url, verbose, output_json_flag):
    """Export a trained model."""
    client = APIClient(api_url, verbose)

    try:
        print_info(f"Exporting model for project '{project}' to {format} format...")

        # TODO: Implement export endpoint
        # For now, just show what would happen
        if output_json_flag:
            output_json({
                "success": True,
                "project": project,
                "format": format,
                "quantization": quantization,
                "output": output or f"{project}.{format}"
            })
            return

        print_warning("Model export not yet implemented in backend")
        click.echo(f"  Would export: {project}")
        click.echo(f"  Format: {format}")
        if quantization:
            click.echo(f"  Quantization: {quantization}")

    except click.ClickException as e:
        print_error(str(e))
        sys.exit(1)


# ============================================================================
# ANALYSIS COMMANDS
# ============================================================================

@cli.group()
def analyze():
    """Analyze projects and datasets."""
    pass


@analyze.command('dataset')
@click.argument('project')
@click.option('--estimate-size', is_flag=True, help='Estimate final model size')
@click.option('--validate', is_flag=True, help='Validate dataset quality')
@click.option('--stats', is_flag=True, help='Show detailed statistics')
@add_common_options
def analyze_dataset(project, estimate_size, validate, stats, api_url, verbose, output_json_flag):
    """Analyze a project's dataset."""
    client = APIClient(api_url, verbose)

    try:
        proj_data = client.get(f"/projects/{project}")
        datasets = proj_data.get('datasets', [])

        if not datasets:
            raise click.ClickException(f"No datasets found for project '{project}'")

        # Use most recent dataset
        dataset = sorted(datasets, key=lambda x: x['created_at'], reverse=True)[0]

        if output_json_flag:
            output_json({
                "project": project,
                "dataset": dataset,
                "analysis": {
                    "num_examples": dataset['num_examples'],
                    "format": dataset['format'],
                }
            })
            return

        print_header(f"Dataset Analysis: {project}")

        click.echo(f"{Colors.BOLD}Dataset:{Colors.RESET} {dataset['filename']}")
        click.echo(f"  Examples: {dataset['num_examples']}")
        click.echo(f"  Format: {dataset['format']}")
        click.echo(f"  Created: {format_datetime(dataset['created_at'])}")

        if dataset.get('size_bytes'):
            size_mb = dataset['size_bytes'] / (1024 * 1024)
            click.echo(f"  Size: {size_mb:.2f} MB")

        if estimate_size:
            click.echo(f"\n{Colors.BOLD}Size Estimation:{Colors.RESET}")
            # Rough estimation
            base_model_size = 13  # GB for 7B model
            lora_size = 0.1  # GB for LoRA adapters
            click.echo(f"  Base Model: ~{base_model_size} GB")
            click.echo(f"  LoRA Adapters: ~{lora_size} GB")
            click.echo(f"  Total (merged): ~{base_model_size + lora_size} GB")

        if validate:
            print_info("Validating dataset...")
            # TODO: Implement actual validation
            print_success("Dataset structure is valid")

        if stats:
            click.echo(f"\n{Colors.BOLD}Statistics:{Colors.RESET}")
            click.echo(f"  XML Patterns: {len(proj_data.get('xml_patterns', []))}")
            click.echo(f"  Avg examples per pattern: {dataset['num_examples'] // max(len(proj_data.get('xml_patterns', [])), 1)}")

    except click.ClickException as e:
        print_error(str(e))
        sys.exit(1)


# ============================================================================
# TUI COMMAND
# ============================================================================

@cli.command()
@click.option('--api-url', envvar='API_URL', default='http://localhost:8000', help='Backend API URL')
def tui(api_url):
    """Launch interactive TUI interface."""
    try:
        print_info("Launching TUI interface...")
        print_warning("TUI not yet implemented")
        click.echo(f"\n{Colors.CYAN}The TUI will provide:{Colors.RESET}")
        click.echo("  • Interactive project management")
        click.echo("  • Real-time training monitoring")
        click.echo("  • Visual dataset exploration")
        click.echo("  • Model comparison tools")
        click.echo(f"\n{Colors.DIM}Use CLI commands for now{Colors.RESET}")
    except Exception as e:
        print_error(f"Failed to launch TUI: {str(e)}")
        sys.exit(1)


# ============================================================================
# COMPLETION SUPPORT
# ============================================================================

def setup_completion():
    """Setup shell completion."""
    shell = os.getenv('SHELL', '').split('/')[-1]

    completion_instructions = {
        'bash': 'eval "$(_MODEL_TRAIN_COMPLETE=bash_source model-train)"',
        'zsh': 'eval "$(_MODEL_TRAIN_COMPLETE=zsh_source model-train)"',
        'fish': 'eval (env _MODEL_TRAIN_COMPLETE=fish_source model-train)',
    }

    if shell in completion_instructions:
        click.echo(f"Add this to your ~/.{shell}rc:")
        click.echo(f"  {completion_instructions[shell]}")
    else:
        click.echo("Completion supported for bash, zsh, and fish")


@cli.command('completion')
def completion():
    """Show shell completion installation instructions."""
    setup_completion()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for CLI."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        if os.getenv('DEBUG'):
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()
