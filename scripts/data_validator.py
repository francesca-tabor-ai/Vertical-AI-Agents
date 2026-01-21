#!/usr/bin/env python3
"""
Data Validator for Vertical AI Agents

Validates data files used in the project:
- Execution logs (CSV)
- Customer configurations (YAML)
- n8n workflow exports (JSON)
- Prompt templates (Markdown)

Usage:
    python scripts/data_validator.py <file_or_directory> [--type TYPE]
    python scripts/data_validator.py customer-configs/
    python scripts/data_validator.py logs.csv --type execution-log
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


class ValidationResult:
    """Container for validation results."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_info(self, message: str) -> None:
        self.info.append(message)

    def print_report(self) -> None:
        status = "✅ VALID" if self.is_valid else "❌ INVALID"
        print(f"\n{status}: {self.file_path}")

        if self.info:
            for msg in self.info:
                print(f"  ℹ️  {msg}")

        if self.warnings:
            for msg in self.warnings:
                print(f"  ⚠️  {msg}")

        if self.errors:
            for msg in self.errors:
                print(f"  ❌ {msg}")


# =============================================================================
# Pydantic Models for Validation
# =============================================================================


class ModelName(str, Enum):
    """Valid Anthropic model names."""

    HAIKU = "haiku"
    HAIKU_45 = "haiku-4.5"
    HAIKU_FULL = "claude-haiku-4-5-20250514"
    SONNET = "sonnet"
    SONNET_45 = "sonnet-4.5"
    SONNET_FULL = "claude-sonnet-4-5-20250514"
    OPUS = "opus"
    OPUS_45 = "opus-4.5"
    OPUS_FULL = "claude-opus-4-5-20250514"


class RateLimitConfig(BaseModel):
    """Rate limit configuration."""

    requests_per_minute: int = Field(ge=1, le=10000)
    tokens_per_minute: int = Field(ge=1, le=1000000)


class BudgetConfig(BaseModel):
    """Budget configuration."""

    monthly_limit_usd: float = Field(ge=0)
    alert_threshold_percent: float = Field(ge=0, le=100, default=80)


class CustomerConfig(BaseModel):
    """Customer configuration schema."""

    customer_id: str = Field(min_length=1, max_length=100)
    customer_name: str = Field(min_length=1, max_length=200)
    model: str = Field(default="claude-sonnet-4-5-20250514")
    max_tokens: int = Field(ge=1, le=200000, default=4096)
    temperature: float = Field(ge=0, le=2, default=0.7)
    prompts: list[str] = Field(default_factory=list)
    rate_limit: Optional[RateLimitConfig] = None
    budget: Optional[BudgetConfig] = None

    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9][a-z0-9\-_]*$", v):
            raise ValueError(
                "customer_id must be lowercase alphanumeric with hyphens/underscores"
            )
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        valid_models = {e.value for e in ModelName}
        if v.lower() not in valid_models:
            raise ValueError(f"Invalid model. Must be one of: {sorted(valid_models)}")
        return v


class ExecutionLogRow(BaseModel):
    """Single row of execution log."""

    timestamp: datetime
    customer_name: str = Field(min_length=1)
    workflow_name: str = Field(min_length=1)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    model: str

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        valid_models = {e.value for e in ModelName}
        if v.lower() not in valid_models:
            raise ValueError(f"Invalid model '{v}'")
        return v.lower()


class N8nWorkflowNode(BaseModel):
    """n8n workflow node schema."""

    id: str
    name: str
    type: str
    position: list[float]
    parameters: dict = Field(default_factory=dict)


class N8nWorkflow(BaseModel):
    """n8n workflow export schema."""

    name: str = Field(min_length=1)
    nodes: list[N8nWorkflowNode] = Field(min_length=1)
    connections: dict = Field(default_factory=dict)
    active: Optional[bool] = None
    settings: Optional[dict] = None

    @model_validator(mode="after")
    def check_node_connections(self) -> "N8nWorkflow":
        """Validate that connections reference existing nodes."""
        node_names = {node.name for node in self.nodes}
        for source_node in self.connections:
            if source_node not in node_names:
                raise ValueError(
                    f"Connection references unknown node: '{source_node}'"
                )
        return self


# =============================================================================
# Validators
# =============================================================================


def validate_customer_config(file_path: Path) -> ValidationResult:
    """Validate a customer configuration YAML file."""
    result = ValidationResult(file_path)

    try:
        with open(file_path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        result.add_error(f"Invalid YAML syntax: {e}")
        return result
    except Exception as e:
        result.add_error(f"Failed to read file: {e}")
        return result

    if data is None:
        result.add_error("File is empty")
        return result

    try:
        config = CustomerConfig(**data)
        result.add_info(f"Customer: {config.customer_name} ({config.customer_id})")
        result.add_info(f"Model: {config.model}, Max tokens: {config.max_tokens}")

        if config.prompts:
            result.add_info(f"Prompts: {', '.join(config.prompts)}")

        if config.budget:
            result.add_info(f"Budget: ${config.budget.monthly_limit_usd}/month")

        # Warnings
        if config.temperature > 1.0:
            result.add_warning(f"High temperature ({config.temperature}) may cause inconsistent outputs")

        if config.max_tokens > 50000:
            result.add_warning(f"High max_tokens ({config.max_tokens}) may increase costs significantly")

        if not config.budget:
            result.add_warning("No budget limits configured")

    except Exception as e:
        result.add_error(f"Validation failed: {e}")

    return result


def validate_execution_log(file_path: Path) -> ValidationResult:
    """Validate an execution log CSV file."""
    result = ValidationResult(file_path)

    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        result.add_error("CSV file is empty")
        return result
    except Exception as e:
        result.add_error(f"Failed to parse CSV: {e}")
        return result

    # Check required columns
    required_columns = [
        "timestamp",
        "customer_name",
        "workflow_name",
        "input_tokens",
        "output_tokens",
        "model",
    ]
    missing = set(required_columns) - set(df.columns)
    if missing:
        result.add_error(f"Missing required columns: {missing}")
        return result

    result.add_info(f"Total rows: {len(df)}")
    result.add_info(f"Customers: {df['customer_name'].nunique()}")
    result.add_info(f"Workflows: {df['workflow_name'].nunique()}")

    # Validate each row
    valid_models = {e.value for e in ModelName}
    invalid_rows = []
    invalid_models = set()

    for idx, row in df.iterrows():
        errors = []

        # Timestamp
        try:
            pd.to_datetime(row["timestamp"])
        except Exception:
            errors.append("invalid timestamp")

        # Tokens
        try:
            if int(row["input_tokens"]) < 0:
                errors.append("negative input_tokens")
        except (ValueError, TypeError):
            errors.append("invalid input_tokens")

        try:
            if int(row["output_tokens"]) < 0:
                errors.append("negative output_tokens")
        except (ValueError, TypeError):
            errors.append("invalid output_tokens")

        # Model
        model = str(row["model"]).lower().strip()
        if model not in valid_models:
            invalid_models.add(row["model"])

        # Empty strings
        if not row["customer_name"] or pd.isna(row["customer_name"]):
            errors.append("empty customer_name")
        if not row["workflow_name"] or pd.isna(row["workflow_name"]):
            errors.append("empty workflow_name")

        if errors:
            invalid_rows.append((idx + 2, errors))  # +2 for header and 0-index

    if invalid_models:
        result.add_warning(f"Unknown models: {invalid_models}")

    if invalid_rows:
        result.add_error(f"Found {len(invalid_rows)} invalid rows")
        for row_num, errors in invalid_rows[:5]:  # Show first 5
            result.add_error(f"  Row {row_num}: {', '.join(errors)}")
        if len(invalid_rows) > 5:
            result.add_error(f"  ... and {len(invalid_rows) - 5} more")
    else:
        result.add_info("All rows valid")

    # Check for anomalies
    if df["input_tokens"].max() > 100000:
        result.add_warning(
            f"Very high input_tokens detected (max: {df['input_tokens'].max()})"
        )

    if df["output_tokens"].max() > 50000:
        result.add_warning(
            f"Very high output_tokens detected (max: {df['output_tokens'].max()})"
        )

    return result


def validate_n8n_workflow(file_path: Path) -> ValidationResult:
    """Validate an n8n workflow JSON export."""
    result = ValidationResult(file_path)

    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        result.add_error(f"Invalid JSON syntax: {e}")
        return result
    except Exception as e:
        result.add_error(f"Failed to read file: {e}")
        return result

    try:
        workflow = N8nWorkflow(**data)
        result.add_info(f"Workflow: {workflow.name}")
        result.add_info(f"Nodes: {len(workflow.nodes)}")

        # List node types
        node_types = [node.type for node in workflow.nodes]
        result.add_info(f"Node types: {', '.join(set(node_types))}")

        # Check for common issues
        if workflow.active is False:
            result.add_warning("Workflow is inactive")

        # Check for Anthropic/Claude nodes
        claude_nodes = [n for n in workflow.nodes if "anthropic" in n.type.lower() or "claude" in n.type.lower()]
        if claude_nodes:
            result.add_info(f"Claude nodes: {len(claude_nodes)}")

        # Check for credentials (should not be in export)
        for node in workflow.nodes:
            if "credentials" in node.parameters:
                result.add_warning(
                    f"Node '{node.name}' may contain credential references"
                )

    except Exception as e:
        result.add_error(f"Validation failed: {e}")

    return result


def validate_prompt_template(file_path: Path) -> ValidationResult:
    """Validate a prompt template markdown file."""
    result = ValidationResult(file_path)

    try:
        content = file_path.read_text()
    except Exception as e:
        result.add_error(f"Failed to read file: {e}")
        return result

    if not content.strip():
        result.add_error("File is empty")
        return result

    result.add_info(f"Size: {len(content)} characters")

    # Check for expected sections
    expected_sections = ["# ", "## "]
    has_headers = any(section in content for section in expected_sections)
    if not has_headers:
        result.add_warning("No markdown headers found")

    # Check for template variables
    variables = re.findall(r"\{(\w+)\}", content)
    if variables:
        unique_vars = set(variables)
        result.add_info(f"Variables: {', '.join(sorted(unique_vars))}")
    else:
        result.add_warning("No template variables found (e.g., {variable_name})")

    # Check for code blocks (prompt content)
    code_blocks = re.findall(r"```[\s\S]*?```", content)
    if code_blocks:
        result.add_info(f"Code blocks: {len(code_blocks)}")
    else:
        result.add_warning("No code blocks found for prompt content")

    # Check for potential issues
    if len(content) > 50000:
        result.add_warning("Very large template (>50k chars)")

    # Check for accidental API keys
    if re.search(r"sk-[a-zA-Z0-9]{20,}", content):
        result.add_error("Possible API key detected in template!")

    return result


# =============================================================================
# File Type Detection and Main Logic
# =============================================================================


class FileType(str, Enum):
    CUSTOMER_CONFIG = "customer-config"
    EXECUTION_LOG = "execution-log"
    N8N_WORKFLOW = "n8n-workflow"
    PROMPT_TEMPLATE = "prompt-template"


def detect_file_type(file_path: Path) -> Optional[FileType]:
    """Auto-detect file type based on extension and location."""
    suffix = file_path.suffix.lower()
    parts = file_path.parts

    # By directory
    if "customer-configs" in parts and suffix in (".yaml", ".yml"):
        return FileType.CUSTOMER_CONFIG
    if "n8n-workflows" in parts and suffix == ".json":
        return FileType.N8N_WORKFLOW
    if "prompts" in parts and suffix == ".md":
        return FileType.PROMPT_TEMPLATE

    # By extension and content hints
    if suffix == ".csv":
        return FileType.EXECUTION_LOG
    if suffix in (".yaml", ".yml"):
        return FileType.CUSTOMER_CONFIG
    if suffix == ".json":
        return FileType.N8N_WORKFLOW
    if suffix == ".md":
        return FileType.PROMPT_TEMPLATE

    return None


def validate_file(file_path: Path, file_type: Optional[FileType] = None) -> ValidationResult:
    """Validate a single file."""
    if file_type is None:
        file_type = detect_file_type(file_path)

    if file_type is None:
        result = ValidationResult(file_path)
        result.add_error(f"Unknown file type. Use --type to specify.")
        return result

    validators = {
        FileType.CUSTOMER_CONFIG: validate_customer_config,
        FileType.EXECUTION_LOG: validate_execution_log,
        FileType.N8N_WORKFLOW: validate_n8n_workflow,
        FileType.PROMPT_TEMPLATE: validate_prompt_template,
    }

    return validators[file_type](file_path)


def validate_directory(dir_path: Path, file_type: Optional[FileType] = None) -> list[ValidationResult]:
    """Validate all applicable files in a directory."""
    results = []

    patterns = {
        FileType.CUSTOMER_CONFIG: ["*.yaml", "*.yml"],
        FileType.EXECUTION_LOG: ["*.csv"],
        FileType.N8N_WORKFLOW: ["*.json"],
        FileType.PROMPT_TEMPLATE: ["*.md"],
    }

    if file_type:
        globs = patterns.get(file_type, [])
    else:
        globs = ["*.yaml", "*.yml", "*.csv", "*.json", "*.md"]

    for glob_pattern in globs:
        for file_path in dir_path.rglob(glob_pattern):
            if file_path.name.startswith("."):
                continue
            results.append(validate_file(file_path, file_type))

    return results


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate data files for Vertical AI Agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
File types:
  customer-config   YAML customer configuration files
  execution-log     CSV execution log files
  n8n-workflow      JSON n8n workflow exports
  prompt-template   Markdown prompt templates

Examples:
  python data_validator.py customer-configs/
  python data_validator.py logs.csv --type execution-log
  python data_validator.py n8n-workflows/my-workflow.json
        """,
    )
    parser.add_argument("path", type=Path, help="File or directory to validate")
    parser.add_argument(
        "--type",
        "-t",
        type=str,
        choices=[t.value for t in FileType],
        help="File type (auto-detected if not specified)",
    )

    args = parser.parse_args()

    if not args.path.exists():
        logger.error(f"Path not found: {args.path}")
        return 1

    file_type = FileType(args.type) if args.type else None

    print("\n" + "=" * 60)
    print("  DATA VALIDATION REPORT")
    print("=" * 60)

    if args.path.is_file():
        results = [validate_file(args.path, file_type)]
    else:
        results = validate_directory(args.path, file_type)

    if not results:
        print("\nNo files found to validate.")
        return 1

    for result in results:
        result.print_report()

    # Summary
    valid_count = sum(1 for r in results if r.is_valid)
    total_count = len(results)
    warning_count = sum(len(r.warnings) for r in results)

    print("\n" + "-" * 60)
    print(f"Summary: {valid_count}/{total_count} files valid", end="")
    if warning_count > 0:
        print(f", {warning_count} warnings")
    else:
        print()
    print("=" * 60 + "\n")

    return 0 if valid_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())
