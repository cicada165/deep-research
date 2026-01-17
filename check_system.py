"""
Quick system status check
"""

from deep_research import SystemStatus

if __name__ == "__main__":
    status = SystemStatus()
    status.print_status()
