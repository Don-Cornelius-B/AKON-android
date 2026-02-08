"""
AKON Agnostic Configuration
Centralized settings for UI theme and Network protocols.
"""

# --- Network Settings ---
UDP_PORT = 5000
BROADCAST_ADDR = '255.255.255.255'
BUFFER_SIZE = 1024

# --- UI Theme (RGBA) ---
DARK_SPACE = (0.02, 0.04, 0.08, 1)    # Deep Midnight Navy
CYBER_BLUE = (0, 0.7, 1, 1)           # Main Accent (Buttons/Header)
MY_BUBBLE = (0, 0.5, 0.8, 0.9)        # Your message color
THEIR_BUBBLE = (0.15, 0.15, 0.2, 0.9) # Incoming message color
TEXT_LIGHT = (0.95, 0.95, 1, 1)       # Clean white text