#!/usr/bin/env python3
"""
Analytics Dashboard for Vertical AI Agents

Track business metrics and generate reports for decision-making.
Supports real-time dashboard, weekly summaries, and monthly reports.

Usage:
    python scripts/analytics_dashboard.py --server --port 8080
    python scripts/analytics_dashboard.py --report monthly --output reports/
    python scripts/analytics_dashboard.py --generate-sample-data
"""

import argparse
import http.server
import json
import logging
import smtplib
import socketserver
import sys
import threading
import webbrowser
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Optional

import pandas as pd

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class Customer:
    """Customer record."""
    customer_id: str
    customer_name: str
    mrr: float
    start_date: datetime
    status: str  # active, churned, trial
    plan: str
    industry: str = ""


@dataclass
class Execution:
    """Workflow execution record."""
    timestamp: datetime
    customer_id: str
    workflow_name: str
    input_tokens: int
    output_tokens: int
    model: str
    cost_usd: float
    status: str  # success, failed
    duration_ms: int = 0


@dataclass
class Revenue:
    """Revenue/payment record."""
    date: datetime
    customer_id: str
    amount: float
    status: str  # paid, failed, refunded


@dataclass
class SupportTicket:
    """Support ticket record."""
    created_at: datetime
    customer_id: str
    subject: str
    status: str  # open, resolved, closed
    resolution_time_hours: Optional[float] = None


@dataclass
class Metrics:
    """Calculated business metrics."""
    # Revenue
    mrr: float = 0.0
    arr: float = 0.0
    mrr_growth_rate: float = 0.0
    arpu: float = 0.0

    # Customers
    total_customers: int = 0
    active_customers: int = 0
    new_customers_this_month: int = 0
    churned_customers_this_month: int = 0
    churn_rate: float = 0.0
    ltv: float = 0.0

    # Usage
    total_executions: int = 0
    executions_per_customer: float = 0.0
    success_rate: float = 0.0
    avg_processing_time_ms: float = 0.0

    # Costs
    total_api_cost: float = 0.0
    cost_per_customer: float = 0.0
    gross_margin: float = 0.0
    gross_margin_pct: float = 0.0

    # Efficiency
    avg_tickets_per_customer: float = 0.0
    avg_resolution_time_hours: float = 0.0

    # Period info
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

    # Breakdowns
    revenue_by_month: dict = field(default_factory=dict)
    customers_by_month: dict = field(default_factory=dict)
    costs_by_month: dict = field(default_factory=dict)
    top_customers: list = field(default_factory=list)
    executions_by_workflow: dict = field(default_factory=dict)
    costs_by_model: dict = field(default_factory=dict)


# =============================================================================
# Data Loaders
# =============================================================================


class DataLoader(ABC):
    """Abstract base class for data loaders."""

    @abstractmethod
    def load_customers(self) -> list[Customer]:
        pass

    @abstractmethod
    def load_executions(self, start_date: datetime, end_date: datetime) -> list[Execution]:
        pass

    @abstractmethod
    def load_revenue(self, start_date: datetime, end_date: datetime) -> list[Revenue]:
        pass

    @abstractmethod
    def load_support_tickets(self, start_date: datetime, end_date: datetime) -> list[SupportTicket]:
        pass


class CSVDataLoader(DataLoader):
    """Load data from CSV files."""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)

    def load_customers(self) -> list[Customer]:
        path = self.data_dir / "customers.csv"
        if not path.exists():
            return []
        df = pd.read_csv(path)
        df['start_date'] = pd.to_datetime(df['start_date'])
        return [
            Customer(
                customer_id=row['customer_id'],
                customer_name=row['customer_name'],
                mrr=row['mrr'],
                start_date=row['start_date'],
                status=row['status'],
                plan=row.get('plan', 'standard'),
                industry=row.get('industry', ''),
            )
            for _, row in df.iterrows()
        ]

    def load_executions(self, start_date: datetime, end_date: datetime) -> list[Execution]:
        path = self.data_dir / "executions.csv"
        if not path.exists():
            # Try sample data
            path = self.data_dir / "sample_execution_logs.csv"
        if not path.exists():
            return []

        df = pd.read_csv(path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]

        # Calculate cost if not present
        if 'cost_usd' not in df.columns:
            df['cost_usd'] = df.apply(lambda r: self._calc_cost(r), axis=1)

        return [
            Execution(
                timestamp=row['timestamp'],
                customer_id=row.get('customer_id', row.get('customer_name', '')),
                workflow_name=row['workflow_name'],
                input_tokens=row['input_tokens'],
                output_tokens=row['output_tokens'],
                model=row['model'],
                cost_usd=row['cost_usd'],
                status=row.get('status', row.get('execution_status', 'success')),
                duration_ms=row.get('duration_ms', 0),
            )
            for _, row in df.iterrows()
        ]

    def _calc_cost(self, row) -> float:
        pricing = {
            'haiku': (0.80, 4.00),
            'sonnet': (3.00, 15.00),
            'opus': (15.00, 75.00),
        }
        model = row['model'].lower()
        for key, (inp, out) in pricing.items():
            if key in model:
                return (row['input_tokens'] / 1_000_000 * inp +
                        row['output_tokens'] / 1_000_000 * out)
        return 0.0

    def load_revenue(self, start_date: datetime, end_date: datetime) -> list[Revenue]:
        path = self.data_dir / "revenue.csv"
        if not path.exists():
            return []
        df = pd.read_csv(path)
        df['date'] = pd.to_datetime(df['date'])
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        return [
            Revenue(
                date=row['date'],
                customer_id=row['customer_id'],
                amount=row['amount'],
                status=row.get('status', 'paid'),
            )
            for _, row in df.iterrows()
        ]

    def load_support_tickets(self, start_date: datetime, end_date: datetime) -> list[SupportTicket]:
        path = self.data_dir / "support_tickets.csv"
        if not path.exists():
            return []
        df = pd.read_csv(path)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df = df[(df['created_at'] >= start_date) & (df['created_at'] <= end_date)]
        return [
            SupportTicket(
                created_at=row['created_at'],
                customer_id=row['customer_id'],
                subject=row['subject'],
                status=row['status'],
                resolution_time_hours=row.get('resolution_time_hours'),
            )
            for _, row in df.iterrows()
        ]


class MockDataLoader(DataLoader):
    """Generate mock data for testing/demo."""

    def __init__(self, seed: int = 42):
        import random
        random.seed(seed)
        self.random = random
        self._customers = self._generate_customers()

    def _generate_customers(self) -> list[Customer]:
        names = [
            ("cust-001", "Acme Corp", 1500, "active", "professional"),
            ("cust-002", "TechStart Inc", 1500, "active", "professional"),
            ("cust-003", "GlobalRetail", 2500, "active", "enterprise"),
            ("cust-004", "HealthFirst", 1500, "active", "professional"),
            ("cust-005", "FinanceFlow", 2500, "active", "enterprise"),
            ("cust-006", "DataDriven Co", 1500, "churned", "professional"),
            ("cust-007", "SmartLogistics", 1500, "active", "professional"),
            ("cust-008", "CloudNine Ltd", 1000, "trial", "starter"),
        ]
        customers = []
        base_date = datetime(2024, 6, 1)
        for i, (cid, name, mrr, status, plan) in enumerate(names):
            start = base_date + timedelta(days=i * 15)
            customers.append(Customer(
                customer_id=cid,
                customer_name=name,
                mrr=mrr,
                start_date=start,
                status=status,
                plan=plan,
                industry=self.random.choice(["SaaS", "Retail", "Healthcare", "Finance"]),
            ))
        return customers

    def load_customers(self) -> list[Customer]:
        return self._customers

    def load_executions(self, start_date: datetime, end_date: datetime) -> list[Execution]:
        executions = []
        workflows = ["expense-analyzer", "lead-scorer", "demand-planner", "doc-classifier"]
        models = ["haiku", "sonnet", "opus"]
        model_weights = [0.6, 0.35, 0.05]

        current = start_date
        while current <= end_date:
            for customer in self._customers:
                if customer.status != "active":
                    continue
                # 5-20 executions per day per customer
                num_execs = self.random.randint(5, 20)
                for _ in range(num_execs):
                    model = self.random.choices(models, weights=model_weights)[0]
                    if model == "opus":
                        inp_tokens = self.random.randint(5000, 30000)
                        out_tokens = self.random.randint(2000, 10000)
                    elif model == "sonnet":
                        inp_tokens = self.random.randint(1000, 15000)
                        out_tokens = self.random.randint(500, 4000)
                    else:
                        inp_tokens = self.random.randint(200, 5000)
                        out_tokens = self.random.randint(100, 2000)

                    cost = self._calc_cost(model, inp_tokens, out_tokens)

                    executions.append(Execution(
                        timestamp=current + timedelta(
                            hours=self.random.randint(8, 18),
                            minutes=self.random.randint(0, 59),
                        ),
                        customer_id=customer.customer_id,
                        workflow_name=self.random.choice(workflows),
                        input_tokens=inp_tokens,
                        output_tokens=out_tokens,
                        model=model,
                        cost_usd=cost,
                        status="success" if self.random.random() > 0.02 else "failed",
                        duration_ms=self.random.randint(500, 5000),
                    ))
            current += timedelta(days=1)
        return executions

    def _calc_cost(self, model: str, inp: int, out: int) -> float:
        pricing = {"haiku": (0.80, 4.00), "sonnet": (3.00, 15.00), "opus": (15.00, 75.00)}
        inp_rate, out_rate = pricing.get(model, (0, 0))
        return inp / 1_000_000 * inp_rate + out / 1_000_000 * out_rate

    def load_revenue(self, start_date: datetime, end_date: datetime) -> list[Revenue]:
        revenue = []
        current = start_date.replace(day=1)
        while current <= end_date:
            for customer in self._customers:
                if customer.start_date <= current and customer.status in ("active", "churned"):
                    status = "paid" if self.random.random() > 0.02 else "failed"
                    revenue.append(Revenue(
                        date=current,
                        customer_id=customer.customer_id,
                        amount=customer.mrr,
                        status=status,
                    ))
            current = (current + timedelta(days=32)).replace(day=1)
        return revenue

    def load_support_tickets(self, start_date: datetime, end_date: datetime) -> list[SupportTicket]:
        tickets = []
        subjects = [
            "Workflow not running",
            "Data format question",
            "Invoice inquiry",
            "Feature request",
            "Integration help",
        ]
        current = start_date
        while current <= end_date:
            for customer in self._customers:
                if customer.status != "active":
                    continue
                # 0-2 tickets per week per customer
                if self.random.random() > 0.7:
                    tickets.append(SupportTicket(
                        created_at=current + timedelta(hours=self.random.randint(9, 17)),
                        customer_id=customer.customer_id,
                        subject=self.random.choice(subjects),
                        status=self.random.choice(["resolved", "closed"]),
                        resolution_time_hours=self.random.uniform(1, 48),
                    ))
            current += timedelta(days=1)
        return tickets


# =============================================================================
# Metrics Calculator
# =============================================================================


class MetricsCalculator:
    """Calculate business metrics from data."""

    def __init__(self, loader: DataLoader):
        self.loader = loader

    def calculate(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Metrics:
        """Calculate all metrics for the given period."""
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        # Load data
        customers = self.loader.load_customers()
        executions = self.loader.load_executions(start_date, end_date)
        revenue = self.loader.load_revenue(start_date, end_date)
        tickets = self.loader.load_support_tickets(start_date, end_date)

        metrics = Metrics(period_start=start_date, period_end=end_date)

        # Customer metrics
        active_customers = [c for c in customers if c.status == "active"]
        metrics.total_customers = len(customers)
        metrics.active_customers = len(active_customers)

        month_start = end_date.replace(day=1)
        metrics.new_customers_this_month = len([
            c for c in customers
            if c.start_date >= month_start and c.status in ("active", "trial")
        ])
        metrics.churned_customers_this_month = len([
            c for c in customers if c.status == "churned"
        ])

        if metrics.active_customers > 0:
            metrics.churn_rate = (
                metrics.churned_customers_this_month /
                (metrics.active_customers + metrics.churned_customers_this_month) * 100
            )

        # Revenue metrics
        metrics.mrr = sum(c.mrr for c in active_customers)
        metrics.arr = metrics.mrr * 12
        metrics.arpu = metrics.mrr / metrics.active_customers if metrics.active_customers > 0 else 0

        # LTV (simplified: ARPU / monthly churn rate)
        monthly_churn = metrics.churn_rate / 100 if metrics.churn_rate > 0 else 0.05
        metrics.ltv = metrics.arpu / monthly_churn if monthly_churn > 0 else metrics.arpu * 24

        # Usage metrics
        metrics.total_executions = len(executions)
        if metrics.active_customers > 0:
            metrics.executions_per_customer = metrics.total_executions / metrics.active_customers

        successful = [e for e in executions if e.status == "success"]
        metrics.success_rate = len(successful) / len(executions) * 100 if executions else 100

        if executions:
            durations = [e.duration_ms for e in executions if e.duration_ms > 0]
            metrics.avg_processing_time_ms = sum(durations) / len(durations) if durations else 0

        # Cost metrics
        metrics.total_api_cost = sum(e.cost_usd for e in executions)
        if metrics.active_customers > 0:
            metrics.cost_per_customer = metrics.total_api_cost / metrics.active_customers
        metrics.gross_margin = metrics.mrr - metrics.total_api_cost
        metrics.gross_margin_pct = (
            metrics.gross_margin / metrics.mrr * 100 if metrics.mrr > 0 else 0
        )

        # Support metrics
        if tickets:
            customer_ticket_counts = {}
            for t in tickets:
                customer_ticket_counts[t.customer_id] = customer_ticket_counts.get(t.customer_id, 0) + 1
            metrics.avg_tickets_per_customer = (
                sum(customer_ticket_counts.values()) / len(customer_ticket_counts)
                if customer_ticket_counts else 0
            )
            resolution_times = [t.resolution_time_hours for t in tickets if t.resolution_time_hours]
            metrics.avg_resolution_time_hours = (
                sum(resolution_times) / len(resolution_times) if resolution_times else 0
            )

        # Breakdowns
        metrics.top_customers = sorted(
            active_customers, key=lambda c: c.mrr, reverse=True
        )[:10]

        # Executions by workflow
        workflow_counts: dict[str, int] = {}
        for e in executions:
            workflow_counts[e.workflow_name] = workflow_counts.get(e.workflow_name, 0) + 1
        metrics.executions_by_workflow = dict(
            sorted(workflow_counts.items(), key=lambda x: x[1], reverse=True)
        )

        # Costs by model
        model_costs: dict[str, float] = {}
        for e in executions:
            model_costs[e.model] = model_costs.get(e.model, 0) + e.cost_usd
        metrics.costs_by_model = dict(
            sorted(model_costs.items(), key=lambda x: x[1], reverse=True)
        )

        # Monthly trends (last 6 months)
        for i in range(6):
            month_end = (end_date.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
            month_start_trend = month_end - timedelta(days=30)
            month_key = month_end.strftime("%Y-%m")

            month_execs = [
                e for e in executions
                if month_start_trend <= e.timestamp < month_end + timedelta(days=31)
            ]
            metrics.costs_by_month[month_key] = sum(e.cost_usd for e in month_execs)

        return metrics


# =============================================================================
# Visualization Generator
# =============================================================================


class ChartGenerator:
    """Generate charts for the dashboard."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self, metrics: Metrics) -> dict[str, str]:
        """Generate all charts and return paths."""
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("matplotlib not available, skipping charts")
            return {}

        charts = {}

        # Revenue overview
        charts['revenue'] = self._revenue_chart(metrics)

        # Cost breakdown
        charts['costs'] = self._cost_chart(metrics)

        # Workflow usage
        charts['workflows'] = self._workflow_chart(metrics)

        # Model costs
        charts['models'] = self._model_chart(metrics)

        return charts

    def _revenue_chart(self, metrics: Metrics) -> str:
        fig, ax = plt.subplots(figsize=(10, 5))

        # Bar chart of key revenue metrics
        labels = ['MRR', 'API Costs', 'Gross Margin']
        values = [metrics.mrr, metrics.total_api_cost, metrics.gross_margin]
        colors = ['#2ecc71', '#e74c3c', '#3498db']

        bars = ax.bar(labels, values, color=colors)
        ax.set_ylabel('USD')
        ax.set_title('Revenue Overview')

        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                   f'${val:,.0f}', ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        path = self.output_dir / 'revenue_chart.png'
        plt.savefig(path, dpi=100, bbox_inches='tight')
        plt.close()
        return str(path)

    def _cost_chart(self, metrics: Metrics) -> str:
        fig, ax = plt.subplots(figsize=(10, 5))

        if metrics.costs_by_month:
            months = list(reversed(list(metrics.costs_by_month.keys())))
            costs = [metrics.costs_by_month[m] for m in months]

            ax.plot(months, costs, marker='o', linewidth=2, color='#e74c3c')
            ax.fill_between(months, costs, alpha=0.3, color='#e74c3c')
            ax.set_ylabel('Cost (USD)')
            ax.set_xlabel('Month')
            ax.set_title('API Cost Trend')
            plt.xticks(rotation=45)

        plt.tight_layout()
        path = self.output_dir / 'cost_chart.png'
        plt.savefig(path, dpi=100, bbox_inches='tight')
        plt.close()
        return str(path)

    def _workflow_chart(self, metrics: Metrics) -> str:
        fig, ax = plt.subplots(figsize=(10, 5))

        if metrics.executions_by_workflow:
            workflows = list(metrics.executions_by_workflow.keys())[:8]
            counts = [metrics.executions_by_workflow[w] for w in workflows]

            colors = plt.cm.Blues([(i+3)/10 for i in range(len(workflows))])
            ax.barh(workflows, counts, color=colors)
            ax.set_xlabel('Executions')
            ax.set_title('Executions by Workflow')

        plt.tight_layout()
        path = self.output_dir / 'workflow_chart.png'
        plt.savefig(path, dpi=100, bbox_inches='tight')
        plt.close()
        return str(path)

    def _model_chart(self, metrics: Metrics) -> str:
        fig, ax = plt.subplots(figsize=(8, 8))

        if metrics.costs_by_model:
            models = list(metrics.costs_by_model.keys())
            costs = list(metrics.costs_by_model.values())
            colors = ['#3498db', '#9b59b6', '#e74c3c'][:len(models)]

            ax.pie(costs, labels=models, autopct='%1.1f%%', colors=colors,
                  explode=[0.02] * len(models))
            ax.set_title('Cost by Model')

        plt.tight_layout()
        path = self.output_dir / 'model_chart.png'
        plt.savefig(path, dpi=100, bbox_inches='tight')
        plt.close()
        return str(path)


# =============================================================================
# Report Generator
# =============================================================================


class ReportGenerator:
    """Generate HTML and PDF reports."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_html_dashboard(
        self,
        metrics: Metrics,
        charts: dict[str, str],
        auto_refresh: bool = False,
    ) -> str:
        """Generate HTML dashboard."""
        refresh_meta = '<meta http-equiv="refresh" content="60">' if auto_refresh else ''

        # Convert chart paths to data URIs or relative paths
        chart_html = ""
        for name, path in charts.items():
            if Path(path).exists():
                chart_html += f'''
                <div class="chart">
                    <img src="{Path(path).name}" alt="{name} chart">
                </div>
                '''

        # Top customers table
        top_customers_rows = ""
        for i, c in enumerate(metrics.top_customers[:10], 1):
            top_customers_rows += f'''
            <tr>
                <td>{i}</td>
                <td>{c.customer_name}</td>
                <td>{c.plan}</td>
                <td>${c.mrr:,.0f}</td>
                <td><span class="status-{c.status}">{c.status}</span></td>
            </tr>
            '''

        # Workflow breakdown
        workflow_rows = ""
        for wf, count in list(metrics.executions_by_workflow.items())[:10]:
            workflow_rows += f'<tr><td>{wf}</td><td>{count:,}</td></tr>'

        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Vertical AI Agents - Analytics Dashboard</title>
    {refresh_meta}
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 10px;
        }}
        header h1 {{ font-size: 2em; margin-bottom: 5px; }}
        header p {{ opacity: 0.9; }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}
        .metric-card h3 {{
            font-size: 0.85em;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 10px;
        }}
        .metric-card .value {{
            font-size: 2em;
            font-weight: 700;
            color: #333;
        }}
        .metric-card .change {{
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        .section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        }}
        .section h2 {{
            font-size: 1.3em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        .chart {{ text-align: center; }}
        .chart img {{ max-width: 100%; height: auto; border-radius: 5px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            color: #666;
        }}
        .status-active {{
            background: #d4edda;
            color: #155724;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.85em;
        }}
        .status-churned {{
            background: #f8d7da;
            color: #721c24;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.85em;
        }}
        .status-trial {{
            background: #fff3cd;
            color: #856404;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.85em;
        }}
        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Analytics Dashboard</h1>
            <p>Vertical AI Agents | {metrics.period_start.strftime('%b %d') if metrics.period_start else ''} - {metrics.period_end.strftime('%b %d, %Y') if metrics.period_end else ''}</p>
        </header>

        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Monthly Recurring Revenue</h3>
                <div class="value">${metrics.mrr:,.0f}</div>
                <div class="change positive">ARR: ${metrics.arr:,.0f}</div>
            </div>
            <div class="metric-card">
                <h3>Active Customers</h3>
                <div class="value">{metrics.active_customers}</div>
                <div class="change">+{metrics.new_customers_this_month} this month</div>
            </div>
            <div class="metric-card">
                <h3>Gross Margin</h3>
                <div class="value">{metrics.gross_margin_pct:.1f}%</div>
                <div class="change positive">${metrics.gross_margin:,.0f}</div>
            </div>
            <div class="metric-card">
                <h3>API Costs</h3>
                <div class="value">${metrics.total_api_cost:,.2f}</div>
                <div class="change">${metrics.cost_per_customer:,.2f}/customer</div>
            </div>
            <div class="metric-card">
                <h3>Total Executions</h3>
                <div class="value">{metrics.total_executions:,}</div>
                <div class="change">{metrics.executions_per_customer:.0f}/customer</div>
            </div>
            <div class="metric-card">
                <h3>Success Rate</h3>
                <div class="value">{metrics.success_rate:.1f}%</div>
                <div class="change">Avg {metrics.avg_processing_time_ms:.0f}ms</div>
            </div>
            <div class="metric-card">
                <h3>Churn Rate</h3>
                <div class="value">{metrics.churn_rate:.1f}%</div>
                <div class="change">{metrics.churned_customers_this_month} churned</div>
            </div>
            <div class="metric-card">
                <h3>Customer LTV</h3>
                <div class="value">${metrics.ltv:,.0f}</div>
                <div class="change">ARPU: ${metrics.arpu:,.0f}</div>
            </div>
        </div>

        <div class="section">
            <h2>Charts</h2>
            <div class="charts-grid">
                {chart_html}
            </div>
        </div>

        <div class="section">
            <h2>Top Customers by MRR</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Customer</th>
                        <th>Plan</th>
                        <th>MRR</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {top_customers_rows}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Workflow Usage</h2>
            <table>
                <thead>
                    <tr>
                        <th>Workflow</th>
                        <th>Executions</th>
                    </tr>
                </thead>
                <tbody>
                    {workflow_rows}
                </tbody>
            </table>
        </div>

        <footer>
            Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Vertical AI Agents
        </footer>
    </div>
</body>
</html>
'''

        path = self.output_dir / 'dashboard.html'
        path.write_text(html)
        logger.info(f"Dashboard generated: {path}")
        return str(path)

    def generate_email_summary(self, metrics: Metrics) -> str:
        """Generate email-friendly summary."""
        return f"""
VERTICAL AI AGENTS - WEEKLY SUMMARY
{'=' * 50}

REVENUE
  MRR: ${metrics.mrr:,.0f}
  ARR: ${metrics.arr:,.0f}
  Gross Margin: {metrics.gross_margin_pct:.1f}% (${metrics.gross_margin:,.0f})

CUSTOMERS
  Active: {metrics.active_customers}
  New this month: {metrics.new_customers_this_month}
  Churn rate: {metrics.churn_rate:.1f}%
  LTV: ${metrics.ltv:,.0f}

USAGE
  Total executions: {metrics.total_executions:,}
  Success rate: {metrics.success_rate:.1f}%
  Avg per customer: {metrics.executions_per_customer:.0f}

COSTS
  Total API cost: ${metrics.total_api_cost:,.2f}
  Per customer: ${metrics.cost_per_customer:,.2f}

TOP WORKFLOWS
{chr(10).join(f'  - {wf}: {count:,} executions' for wf, count in list(metrics.executions_by_workflow.items())[:5])}

---
Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""


# =============================================================================
# Dashboard Server
# =============================================================================


class DashboardServer:
    """Simple HTTP server for the dashboard."""

    def __init__(self, output_dir: Path, port: int = 8080):
        self.output_dir = Path(output_dir)
        self.port = port
        self.server = None

    def start(self, open_browser: bool = True):
        """Start the dashboard server."""
        handler = lambda *args: http.server.SimpleHTTPRequestHandler(
            *args, directory=str(self.output_dir)
        )

        self.server = socketserver.TCPServer(("", self.port), handler)

        url = f"http://localhost:{self.port}/dashboard.html"
        logger.info(f"Dashboard server started at {url}")

        if open_browser:
            threading.Timer(1, lambda: webbrowser.open(url)).start()

        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped")
            self.server.shutdown()


# =============================================================================
# Sample Data Generator
# =============================================================================


def generate_sample_data(output_dir: Path) -> None:
    """Generate sample CSV files for testing."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Customers
    customers_df = pd.DataFrame([
        {"customer_id": "cust-001", "customer_name": "Acme Corp", "mrr": 1500,
         "start_date": "2024-06-01", "status": "active", "plan": "professional", "industry": "SaaS"},
        {"customer_id": "cust-002", "customer_name": "TechStart Inc", "mrr": 1500,
         "start_date": "2024-06-15", "status": "active", "plan": "professional", "industry": "Tech"},
        {"customer_id": "cust-003", "customer_name": "GlobalRetail", "mrr": 2500,
         "start_date": "2024-07-01", "status": "active", "plan": "enterprise", "industry": "Retail"},
        {"customer_id": "cust-004", "customer_name": "HealthFirst", "mrr": 1500,
         "start_date": "2024-07-15", "status": "active", "plan": "professional", "industry": "Healthcare"},
        {"customer_id": "cust-005", "customer_name": "FinanceFlow", "mrr": 2500,
         "start_date": "2024-08-01", "status": "active", "plan": "enterprise", "industry": "Finance"},
        {"customer_id": "cust-006", "customer_name": "DataDriven Co", "mrr": 1500,
         "start_date": "2024-08-15", "status": "churned", "plan": "professional", "industry": "Tech"},
    ])
    customers_df.to_csv(output_dir / "customers.csv", index=False)

    # Revenue
    revenue_records = []
    for _, c in customers_df.iterrows():
        for month in range(6):
            date = (datetime(2024, 7, 1) + timedelta(days=month * 30)).strftime("%Y-%m-01")
            if c['status'] == 'active' or month < 4:
                revenue_records.append({
                    "date": date,
                    "customer_id": c['customer_id'],
                    "amount": c['mrr'],
                    "status": "paid",
                })
    pd.DataFrame(revenue_records).to_csv(output_dir / "revenue.csv", index=False)

    # Support tickets
    import random
    random.seed(42)
    tickets = []
    subjects = ["Setup help", "Data question", "Feature request", "Bug report"]
    for i in range(20):
        tickets.append({
            "created_at": (datetime(2024, 12, 1) + timedelta(days=random.randint(0, 30))).isoformat(),
            "customer_id": f"cust-00{random.randint(1, 5)}",
            "subject": random.choice(subjects),
            "status": "resolved",
            "resolution_time_hours": random.uniform(2, 24),
        })
    pd.DataFrame(tickets).to_csv(output_dir / "support_tickets.csv", index=False)

    logger.info(f"Sample data generated in {output_dir}")
    print(f"\nSample data files created:")
    print(f"  - {output_dir}/customers.csv")
    print(f"  - {output_dir}/revenue.csv")
    print(f"  - {output_dir}/support_tickets.csv")


# =============================================================================
# Main
# =============================================================================


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analytics Dashboard for Vertical AI Agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analytics_dashboard.py --server --port 8080
  python analytics_dashboard.py --report monthly --output reports/
  python analytics_dashboard.py --summary
  python analytics_dashboard.py --generate-sample-data
        """,
    )
    parser.add_argument("--server", action="store_true", help="Start dashboard web server")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    parser.add_argument("--report", choices=["weekly", "monthly"], help="Generate report")
    parser.add_argument("--output", "-o", type=Path, default=Path("reports"), help="Output directory")
    parser.add_argument("--summary", action="store_true", help="Print terminal summary")
    parser.add_argument("--data-dir", type=Path, default=Path("tests"), help="Data directory")
    parser.add_argument("--use-mock", action="store_true", help="Use mock data for demo")
    parser.add_argument("--generate-sample-data", action="store_true", help="Generate sample CSV files")
    parser.add_argument("--days", type=int, default=30, help="Analysis period in days")

    args = parser.parse_args()

    # Generate sample data mode
    if args.generate_sample_data:
        generate_sample_data(args.data_dir)
        return 0

    # Select data loader
    if args.use_mock:
        loader = MockDataLoader()
        logger.info("Using mock data")
    else:
        loader = CSVDataLoader(args.data_dir)
        logger.info(f"Loading data from {args.data_dir}")

    # Calculate metrics
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)

    calculator = MetricsCalculator(loader)
    metrics = calculator.calculate(start_date, end_date)

    # Generate charts
    chart_gen = ChartGenerator(args.output)
    charts = chart_gen.generate_all(metrics)

    # Generate reports
    report_gen = ReportGenerator(args.output)

    if args.summary or (not args.server and not args.report):
        print(report_gen.generate_email_summary(metrics))

    if args.report or args.server:
        dashboard_path = report_gen.generate_html_dashboard(
            metrics, charts, auto_refresh=args.server
        )
        print(f"\nDashboard generated: {dashboard_path}")

    if args.server:
        server = DashboardServer(args.output, args.port)
        server.start(open_browser=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
