"""
AKON Agnostic Configuration
Centralized settings for UI theme and Network protocols.
"""

# --- Network Settings ---
# Standard UDP port for the mesh network
UDP_PORT = 5000 
# Global broadcast address for local peer discovery
BROADCAST_ADDR = '255.255.255.255' 
BUFFER_SIZE = 1024

# --- UI Theme (RGBA) ---
DARK_SPACE = (0.02, 0.04, 0.08, 1)     # Deep Midnight Navy
CYBER_BLUE = (0, 0.7, 1, 1)           # Main Accent (Buttons/Header)

# Message Bubble Colors optimized for white text
MY_BUBBLE = (0, 0.5, 0.8, 0.9)        # Solid Blue for outgoing
THEIR_BUBBLE = (0.15, 0.15, 0.2, 0.9) # Dark Grey for incoming

# Text Colors
TEXT_LIGHT = (0.95, 0.95, 1, 1)       # High-contrast white text