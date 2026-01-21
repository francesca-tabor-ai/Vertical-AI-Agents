#!/usr/bin/env python3
"""
Cost Tracker for Vertical AI Agents

Analyzes n8n execution logs and calculates Anthropic API costs per customer.
Generates terminal summaries and CSV reports for billing analysis.

Usage:
    python scripts/cost_tracker.py <input_csv> [--output <output_csv>] [--month YYYY-MM]
    python scripts/cost_tracker.py --generate-sample  # Generate sample data for testing
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Anthropic pricing per 1M tokens (as of 2025)
PRICING = {
    # Haiku 4.5
    "claude-haiku-4-5-20250514": {"input": 0.80, "output": 4.00},
    "haiku-4.5": {"input": 0.80, "output": 4.00},
    "haiku": {"input": 0.80, "output": 4.00},
    # Sonnet 4.5
    "claude-sonnet-4-5-20250514": {"input": 3.00, "output": 15.00},
    "sonnet-4.5": {"input": 3.00, "output": 15.00},
    "sonnet": {"input": 3.00, "output": 15.00},
    # Opus 4.5
    "claude-opus-4-5-20250514": {"input": 15.00, "output": 75.00},
    "opus-4.5": {"input": 15.00, "output": 75.00},
    "opus": {"input": 15.00, "output": 75.00},
}

# Default monthly price charged per customer
DEFAULT_MONTHLY_PRICE = 1500.00

# Required CSV columns
REQUIRED_COLUMNS = [
    "timestamp",
    "customer_name",
    "workflow_name",
    "input_tokens",
    "output_tokens",
    "model",
]


class CostTrackerError(Exception):
    """Base exception for cost tracker errors."""

    pass


class InvalidCSVError(CostTrackerError):
    """Raised when CSV format is invalid."""

    pass


class UnknownModelError(CostTrackerError):
    """Raised when an unknown model is encountered."""

    pass


def load_execution_logs(csv_path: Path) -> pd.DataFrame:
    """
    Load and validate n8n execution logs from CSV.

    Args:
        csv_path: Path to the CSV file

    Returns:
        DataFrame with execution logs

    Raises:
        InvalidCSVError: If CSV is missing required columns or is malformed
    """
    if not csv_path.exists():
        raise InvalidCSVError(f"File not found: {csv_path}")

    try:
        df = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError:
        raise InvalidCSVError(f"CSV file is empty: {csv_path}")
    except pd.errors.ParserError as e:
        raise InvalidCSVError(f"Failed to parse CSV: {e}")

    # Validate required columns
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_columns:
        raise InvalidCSVError(f"Missing required columns: {missing_columns}")

    # Parse timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    invalid_timestamps = df["timestamp"].isna().sum()
    if invalid_timestamps > 0:
        logger.warning(f"Found {invalid_timestamps} rows with invalid timestamps")

    # Normalize model names to lowercase
    df["model"] = df["model"].str.lower().str.strip()

    # Validate numeric columns
    for col in ["input_tokens", "output_tokens"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    logger.info(f"Loaded {len(df)} execution records from {csv_path}")
    return df


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate cost for a single API call.

    Args:
        model: Model name/identifier
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in USD

    Raises:
        UnknownModelError: If model is not in pricing table
    """
    model_lower = model.lower().strip()

    if model_lower not in PRICING:
        raise UnknownModelError(f"Unknown model: {model}")

    pricing = PRICING[model_lower]
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]

    return input_cost + output_cost


def add_cost_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add cost calculations to DataFrame.

    Args:
        df: DataFrame with execution logs

    Returns:
        DataFrame with added 'cost_usd' column
    """
    costs = []
    unknown_models = set()

    for _, row in df.iterrows():
        try:
            cost = calculate_cost(
                row["model"], row["input_tokens"], row["output_tokens"]
            )
            costs.append(cost)
        except UnknownModelError:
            unknown_models.add(row["model"])
            costs.append(0.0)

    if unknown_models:
        logger.warning(f"Unknown models (cost set to $0): {unknown_models}")

    df = df.copy()
    df["cost_usd"] = costs
    return df


def filter_by_month(df: pd.DataFrame, month: Optional[str] = None) -> pd.DataFrame:
    """
    Filter DataFrame to a specific month.

    Args:
        df: DataFrame with timestamp column
        month: Month in YYYY-MM format, or None for all data

    Returns:
        Filtered DataFrame
    """
    if month is None:
        return df

    try:
        year, month_num = map(int, month.split("-"))
        mask = (df["timestamp"].dt.year == year) & (df["timestamp"].dt.month == month_num)
        filtered = df[mask].copy()
        logger.info(f"Filtered to {len(filtered)} records for {month}")
        return filtered
    except (ValueError, AttributeError) as e:
        logger.error(f"Invalid month format '{month}', expected YYYY-MM: {e}")
        return df


def generate_customer_summary(df: pd.DataFrame, monthly_price: float) -> pd.DataFrame:
    """
    Generate per-customer cost summary with margin analysis.

    Args:
        df: DataFrame with cost data
        monthly_price: Monthly price charged to customers

    Returns:
        DataFrame with customer summary
    """
    summary = (
        df.groupby("customer_name")
        .agg(
            total_runs=("cost_usd", "count"),
            total_input_tokens=("input_tokens", "sum"),
            total_output_tokens=("output_tokens", "sum"),
            total_cost_usd=("cost_usd", "sum"),
        )
        .reset_index()
    )

    summary["avg_cost_per_run"] = summary["total_cost_usd"] / summary["total_runs"]
    summary["monthly_revenue"] = monthly_price
    summary["gross_margin_usd"] = summary["monthly_revenue"] - summary["total_cost_usd"]
    summary["gross_margin_pct"] = (
        summary["gross_margin_usd"] / summary["monthly_revenue"] * 100
    )

    return summary.sort_values("total_cost_usd", ascending=False)


def generate_workflow_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate per-workflow cost summary.

    Args:
        df: DataFrame with cost data

    Returns:
        DataFrame with workflow summary sorted by total cost
    """
    summary = (
        df.groupby(["customer_name", "workflow_name"])
        .agg(
            total_runs=("cost_usd", "count"),
            total_input_tokens=("input_tokens", "sum"),
            total_output_tokens=("output_tokens", "sum"),
            total_cost_usd=("cost_usd", "sum"),
            avg_cost_per_run=("cost_usd", "mean"),
        )
        .reset_index()
    )

    return summary.sort_values("total_cost_usd", ascending=False)


def generate_model_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate per-model usage summary.

    Args:
        df: DataFrame with cost data

    Returns:
        DataFrame with model usage summary
    """
    summary = (
        df.groupby("model")
        .agg(
            total_runs=("cost_usd", "count"),
            total_input_tokens=("input_tokens", "sum"),
            total_output_tokens=("output_tokens", "sum"),
            total_cost_usd=("cost_usd", "sum"),
        )
        .reset_index()
    )

    return summary.sort_values("total_cost_usd", ascending=False)


def print_terminal_report(
    df: pd.DataFrame,
    customer_summary: pd.DataFrame,
    workflow_summary: pd.DataFrame,
    model_summary: pd.DataFrame,
    monthly_price: float,
    month: Optional[str] = None,
) -> None:
    """Print formatted report to terminal."""
    period = month if month else "All Time"

    print("\n" + "=" * 70)
    print(f"  VERTICAL AI AGENTS - COST ANALYSIS REPORT")
    print(f"  Period: {period}")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Overall summary
    total_cost = df["cost_usd"].sum()
    total_runs = len(df)
    total_customers = df["customer_name"].nunique()
    total_revenue = total_customers * monthly_price
    total_margin = total_revenue - total_cost

    print("\n📊 OVERALL SUMMARY")
    print("-" * 40)
    print(f"  Total Executions:     {total_runs:,}")
    print(f"  Total Customers:      {total_customers}")
    print(f"  Total API Cost:       ${total_cost:,.2f}")
    print(f"  Total Revenue:        ${total_revenue:,.2f}")
    print(f"  Gross Margin:         ${total_margin:,.2f} ({total_margin/total_revenue*100:.1f}%)")
    print(f"  Avg Cost/Run:         ${total_cost/total_runs:.4f}" if total_runs > 0 else "")

    # Customer breakdown
    print("\n👥 COST PER CUSTOMER")
    print("-" * 70)
    print(f"{'Customer':<25} {'Runs':>8} {'Cost':>12} {'Margin':>12} {'Margin %':>10}")
    print("-" * 70)

    for _, row in customer_summary.iterrows():
        margin_color = "" if row["gross_margin_pct"] >= 50 else "⚠️ "
        print(
            f"{row['customer_name']:<25} "
            f"{row['total_runs']:>8,} "
            f"${row['total_cost_usd']:>10,.2f} "
            f"${row['gross_margin_usd']:>10,.2f} "
            f"{margin_color}{row['gross_margin_pct']:>8.1f}%"
        )

    # Most expensive workflows
    print("\n🔥 TOP 10 MOST EXPENSIVE WORKFLOWS")
    print("-" * 80)
    print(f"{'Customer':<20} {'Workflow':<25} {'Runs':>8} {'Total Cost':>12} {'Avg Cost':>10}")
    print("-" * 80)

    for _, row in workflow_summary.head(10).iterrows():
        print(
            f"{row['customer_name']:<20} "
            f"{row['workflow_name'][:24]:<25} "
            f"{row['total_runs']:>8,} "
            f"${row['total_cost_usd']:>10,.2f} "
            f"${row['avg_cost_per_run']:>8,.4f}"
        )

    # Model usage
    print("\n🤖 USAGE BY MODEL")
    print("-" * 60)
    print(f"{'Model':<30} {'Runs':>10} {'Cost':>15}")
    print("-" * 60)

    for _, row in model_summary.iterrows():
        print(
            f"{row['model']:<30} "
            f"{row['total_runs']:>10,} "
            f"${row['total_cost_usd']:>13,.2f}"
        )

    # Margin alerts
    low_margin_customers = customer_summary[customer_summary["gross_margin_pct"] < 50]
    if not low_margin_customers.empty:
        print("\n⚠️  MARGIN ALERTS (< 50%)")
        print("-" * 40)
        for _, row in low_margin_customers.iterrows():
            print(f"  {row['customer_name']}: {row['gross_margin_pct']:.1f}% margin (${row['total_cost_usd']:.2f} cost)")

    print("\n" + "=" * 70 + "\n")


def export_csv_report(
    customer_summary: pd.DataFrame,
    workflow_summary: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Export summaries to CSV files for Google Sheets import.

    Args:
        customer_summary: Customer summary DataFrame
        workflow_summary: Workflow summary DataFrame
        output_path: Base path for output files
    """
    # Customer summary
    customer_path = output_path.parent / f"{output_path.stem}_customers.csv"
    customer_summary.to_csv(customer_path, index=False)
    logger.info(f"Customer summary exported to: {customer_path}")

    # Workflow summary
    workflow_path = output_path.parent / f"{output_path.stem}_workflows.csv"
    workflow_summary.to_csv(workflow_path, index=False)
    logger.info(f"Workflow summary exported to: {workflow_path}")

    print(f"\n📁 Reports exported:")
    print(f"   - {customer_path}")
    print(f"   - {workflow_path}")


def generate_sample_data(output_path: Path) -> None:
    """
    Generate sample execution log data for testing.

    Args:
        output_path: Path to write sample CSV
    """
    import random
    from datetime import timedelta

    customers = ["Acme Corp", "TechStart Inc", "GlobalRetail", "HealthFirst", "FinanceFlow"]
    workflows = [
        "document-classification",
        "email-extraction",
        "customer-support",
        "data-validation",
        "report-generation",
        "sentiment-analysis",
    ]
    models = ["haiku", "sonnet", "opus"]
    model_weights = [0.6, 0.35, 0.05]  # Most use haiku, few use opus

    records = []
    base_date = datetime(2025, 1, 1)

    for _ in range(500):
        customer = random.choice(customers)
        workflow = random.choice(workflows)
        model = random.choices(models, weights=model_weights)[0]

        # Token counts vary by model (opus tends to be used for complex tasks)
        if model == "opus":
            input_tokens = random.randint(5000, 50000)
            output_tokens = random.randint(2000, 20000)
        elif model == "sonnet":
            input_tokens = random.randint(1000, 20000)
            output_tokens = random.randint(500, 5000)
        else:
            input_tokens = random.randint(200, 5000)
            output_tokens = random.randint(100, 2000)

        timestamp = base_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        records.append(
            {
                "timestamp": timestamp.isoformat(),
                "customer_name": customer,
                "workflow_name": workflow,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model": model,
            }
        )

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    logger.info(f"Generated {len(records)} sample records at {output_path}")
    print(f"\n✅ Sample data generated: {output_path}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze n8n execution logs and calculate Anthropic API costs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cost_tracker.py logs.csv
  python cost_tracker.py logs.csv --output report.csv --month 2025-01
  python cost_tracker.py --generate-sample
        """,
    )
    parser.add_argument("input_csv", nargs="?", help="Path to execution logs CSV")
    parser.add_argument(
        "--output", "-o", type=Path, help="Output path for CSV reports"
    )
    parser.add_argument(
        "--month", "-m", help="Filter to specific month (YYYY-MM format)"
    )
    parser.add_argument(
        "--price",
        "-p",
        type=float,
        default=DEFAULT_MONTHLY_PRICE,
        help=f"Monthly price per customer (default: ${DEFAULT_MONTHLY_PRICE})",
    )
    parser.add_argument(
        "--generate-sample",
        action="store_true",
        help="Generate sample data for testing",
    )

    args = parser.parse_args()

    # Generate sample data mode
    if args.generate_sample:
        sample_path = Path("tests/sample_execution_logs.csv")
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        generate_sample_data(sample_path)
        return 0

    # Validate input
    if not args.input_csv:
        parser.print_help()
        print("\nError: input_csv is required (or use --generate-sample)")
        return 1

    input_path = Path(args.input_csv)

    try:
        # Load and process data
        df = load_execution_logs(input_path)
        df = add_cost_column(df)
        df = filter_by_month(df, args.month)

        if df.empty:
            logger.warning("No data to analyze after filtering")
            return 1

        # Generate summaries
        customer_summary = generate_customer_summary(df, args.price)
        workflow_summary = generate_workflow_summary(df)
        model_summary = generate_model_summary(df)

        # Print terminal report
        print_terminal_report(
            df, customer_summary, workflow_summary, model_summary, args.price, args.month
        )

        # Export CSV if requested
        if args.output:
            export_csv_report(customer_summary, workflow_summary, args.output)

        return 0

    except CostTrackerError as e:
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
