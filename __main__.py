"""
Pulsus Agent - Main entry point for running as a module.

Usage:
    python -m agents.pulsus                    # Interactive mode with greeting
    python -m agents.pulsus "your request"     # Single-shot mode
    python -m agents.pulsus --quiet            # Skip greeting
    python -m agents.pulsus --ping             # Health check
    python -m agents.pulsus --help             # Show all options

When run, Pulsus automatically introduces himself with capabilities and examples.
"""

from console.interface import main

if __name__ == "__main__":
    main()
