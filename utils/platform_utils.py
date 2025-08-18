"""
Platform Utilities
Cross-platform compatibility helpers
"""
import sys
import os

def is_windows():
    """Check if running on Windows"""
    return sys.platform == "win32"

def is_streamlit_cloud():
    """Check if running on Streamlit Cloud"""
    return (
        os.environ.get('STREAMLIT_SHARING_MODE') is not None or
        os.environ.get('STREAMLIT_CLOUD') is not None or
        'streamlit.app' in os.environ.get('HOSTNAME', '') or
        '/mount/src' in os.getcwd()
    )

def get_desktop_notification_support():
    """Check what desktop notification systems are available"""
    if is_streamlit_cloud():
        return None  # No desktop notifications on cloud
    
    if is_windows():
        try:
            import win10toast
            return 'win10toast'
        except ImportError:
            return None
    else:
        # Could add Linux notification support here (notify-send, etc.)
        return None

def get_notification_capabilities():
    """Get all available notification channels"""
    capabilities = {
        'desktop': get_desktop_notification_support() is not None,
        'email': True,  # Email works everywhere
        'slack': True,  # Slack works everywhere with webhooks
        'platform': sys.platform,
        'is_cloud': is_streamlit_cloud()
    }
    return capabilities