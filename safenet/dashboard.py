"""
SafeNet Dashboard

Web-based dashboard for monitoring MCP operations, performance metrics,
and system health.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

# Try to import Flask, but make it optional
try:
    from flask import Flask, render_template, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None

from mcp.monitoring.metrics import get_metrics
from mcp.monitoring.alerts import get_alert_manager


# Create Flask app if available
if FLASK_AVAILABLE:
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
else:
    app = None


def create_app():
    """
    Create Flask application.

    Returns:
        Flask app or None if Flask not available
    """
    if not FLASK_AVAILABLE:
        print("Flask is not installed. Install with: pip install flask")
        return None

    return app


# Dashboard routes
if FLASK_AVAILABLE:

    @app.route('/')
    def dashboard():
        """Main SafeNet dashboard"""
        metrics = get_metrics()
        alerts = get_alert_manager()

        # Get summary data
        domain_summary = metrics.get_domain_summary()
        recent_operations = metrics.get_recent_operations(limit=50)
        alert_history = alerts.get_history(limit=50)
        alert_counts = alerts.get_alert_counts()

        # Calculate overall statistics
        overall_stats = {
            'total_operations': sum(d['total_operations'] for d in domain_summary.values()),
            'total_domains': len(domain_summary),
            'total_alerts': sum(alert_counts.values()),
            'critical_alerts': alert_counts.get('critical', 0)
        }

        return render_template(
            'dashboard.html',
            domain_summary=domain_summary,
            recent_operations=recent_operations,
            alert_history=alert_history,
            alert_counts=alert_counts,
            overall_stats=overall_stats
        )

    @app.route('/api/metrics')
    def api_metrics():
        """API endpoint for metrics"""
        metrics = get_metrics()

        domain = request.args.get('domain')
        operation = request.args.get('operation')
        timeframe = request.args.get('timeframe', 'all')

        stats = metrics.get_statistics(
            domain=domain,
            operation=operation,
            timeframe=timeframe
        )

        return jsonify(stats)

    @app.route('/api/metrics/recent')
    def api_recent_metrics():
        """API endpoint for recent operations"""
        metrics = get_metrics()

        limit = int(request.args.get('limit', 50))
        domain = request.args.get('domain')

        recent = metrics.get_recent_operations(limit=limit, domain=domain)

        return jsonify({
            'operations': recent,
            'count': len(recent)
        })

    @app.route('/api/metrics/domains')
    def api_domain_summary():
        """API endpoint for domain summary"""
        metrics = get_metrics()
        summary = metrics.get_domain_summary()

        return jsonify(summary)

    @app.route('/api/metrics/slow')
    def api_slow_operations():
        """API endpoint for slow operations"""
        metrics = get_metrics()

        threshold = float(request.args.get('threshold', 1000))
        limit = int(request.args.get('limit', 10))

        slow_ops = metrics.get_slow_operations(
            threshold_ms=threshold,
            limit=limit
        )

        return jsonify({
            'operations': slow_ops,
            'count': len(slow_ops),
            'threshold_ms': threshold
        })

    @app.route('/api/alerts')
    def api_alerts():
        """API endpoint for alerts"""
        alerts = get_alert_manager()

        limit = int(request.args.get('limit', 50))
        severity = request.args.get('severity')

        from mcp.monitoring.alerts import AlertSeverity
        severity_filter = None
        if severity:
            try:
                severity_filter = AlertSeverity(severity)
            except ValueError:
                pass

        history = alerts.get_history(limit=limit, severity=severity_filter)

        return jsonify({
            'alerts': history,
            'count': len(history)
        })

    @app.route('/api/alerts/counts')
    def api_alert_counts():
        """API endpoint for alert counts"""
        alerts = get_alert_manager()
        counts = alerts.get_alert_counts()

        return jsonify(counts)

    @app.route('/domain/<domain_name>')
    def domain_detail(domain_name: str):
        """Domain-specific view"""
        metrics = get_metrics()

        stats = metrics.get_statistics(domain=domain_name)
        recent = metrics.get_recent_operations(limit=100, domain=domain_name)

        return render_template(
            'domain_detail.html',
            domain_name=domain_name,
            stats=stats,
            recent_operations=recent
        )

    @app.route('/health')
    def health():
        """Health check endpoint"""
        metrics = get_metrics()
        alerts = get_alert_manager()

        # Calculate health metrics
        error_rate = metrics.get_error_rate(timeframe='last_hour')
        critical_alerts = alerts.get_alert_counts().get('critical', 0)

        health_status = 'healthy'
        if critical_alerts > 0:
            health_status = 'critical'
        elif error_rate > 0.1:
            health_status = 'degraded'

        return jsonify({
            'status': health_status,
            'error_rate': error_rate,
            'critical_alerts': critical_alerts,
            'timestamp': get_metrics().export_metrics()[-1]['timestamp'] if get_metrics().export_metrics() else None
        })


def run_dashboard(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """
    Run the SafeNet dashboard server.

    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode

    Example:
        >>> from safenet.dashboard import run_dashboard
        >>> run_dashboard(port=5000, debug=True)
    """
    if not FLASK_AVAILABLE:
        print("Error: Flask is not installed.")
        print("Install with: pip install flask")
        return

    if not app:
        print("Error: Flask app not initialized")
        return

    # Check if templates exist
    templates_dir = Path(__file__).parent / 'templates'
    if not templates_dir.exists():
        print(f"Warning: Templates directory not found at {templates_dir}")
        print("Creating basic template...")
        templates_dir.mkdir(exist_ok=True)
        create_basic_template(templates_dir)

    print(f"Starting SafeNet Dashboard on http://{host}:{port}")
    print("Press Ctrl+C to stop")

    app.run(host=host, port=port, debug=debug)


def create_basic_template(templates_dir: Path):
    """
    Create a basic HTML template.

    Args:
        templates_dir: Path to templates directory
    """
    template_html = """<!DOCTYPE html>
<html>
<head>
    <title>SafeNet Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 4px;
            border-left: 4px solid #007bff;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #007bff;
            color: white;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .success {
            color: #28a745;
            font-weight: bold;
        }
        .error {
            color: #dc3545;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ SafeNet Dashboard</h1>

        <h2>Overview</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ overall_stats.total_operations }}</div>
                <div class="stat-label">Total Operations</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ overall_stats.total_domains }}</div>
                <div class="stat-label">Active Domains</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ overall_stats.total_alerts }}</div>
                <div class="stat-label">Total Alerts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ overall_stats.critical_alerts }}</div>
                <div class="stat-label">Critical Alerts</div>
            </div>
        </div>

        <h2>Domain Summary</h2>
        <table>
            <thead>
                <tr>
                    <th>Domain</th>
                    <th>Operations</th>
                    <th>Success Rate</th>
                    <th>Avg Duration (ms)</th>
                </tr>
            </thead>
            <tbody>
                {% for domain, stats in domain_summary.items() %}
                <tr>
                    <td><strong>{{ domain }}</strong></td>
                    <td>{{ stats.total_operations }}</td>
                    <td class="{{ 'success' if stats.success_rate > 0.9 else 'error' }}">
                        {{ "%.1f"|format(stats.success_rate * 100) }}%
                    </td>
                    <td>{{ "%.2f"|format(stats.avg_duration_ms) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <h2>Recent Operations</h2>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Domain</th>
                    <th>Operation</th>
                    <th>Duration (ms)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for op in recent_operations[:20] %}
                <tr>
                    <td>{{ op.timestamp }}</td>
                    <td>{{ op.domain }}</td>
                    <td>{{ op.operation }}</td>
                    <td>{{ "%.2f"|format(op.duration_ms) }}</td>
                    <td class="{{ 'success' if op.success else 'error' }}">
                        {{ 'SUCCESS' if op.success else 'FAILED' }}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>"""

    template_path = templates_dir / 'dashboard.html'
    with open(template_path, 'w') as f:
        f.write(template_html)

    print(f"Created template at {template_path}")


# CLI entry point
if __name__ == '__main__':
    run_dashboard(debug=True)
