"""
Quick system status check
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from deep_research import SystemStatus

if __name__ == "__main__":
    status = SystemStatus()
    status.print_status()
