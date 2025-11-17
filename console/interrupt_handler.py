"""
Interrupt handler for Pulsus console.
Provides ESC key detection for graceful interruption of long-running operations.
"""

import sys
import threading
from typing import Optional

# Platform-specific imports
if sys.platform == 'win32':
    import msvcrt
else:
    import tty
    import termios
    import select


class InterruptHandler:
    """
    Handles ESC key detection for graceful interruption.
    Works on both Windows and Unix-like systems.
    """

    def __init__(self):
        self._interrupted = False
        self._listener_thread: Optional[threading.Thread] = None
        self._stop_listening = threading.Event()
        self._original_settings = None

    def is_interrupted(self) -> bool:
        """Check if ESC key was pressed."""
        return self._interrupted

    def reset(self):
        """Reset interrupt flag."""
        self._interrupted = False

    def start_listening(self):
        """Start listening for ESC key in background thread."""
        self.reset()
        self._stop_listening.clear()

        self._listener_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self._listener_thread.start()

    def stop_listening(self):
        """Stop listening for ESC key."""
        self._stop_listening.set()
        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=0.5)
        self._restore_terminal()

    def _listen_loop(self):
        """Background loop that listens for ESC key press."""
        try:
            if sys.platform == 'win32':
                self._listen_windows()
            else:
                self._listen_unix()
        except Exception:
            # Silently ignore errors in listener thread
            pass

    def _listen_windows(self):
        """Windows-specific ESC detection using msvcrt."""
        while not self._stop_listening.is_set():
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                # ESC key code is 27 (0x1b)
                if ch == b'\x1b':
                    self._interrupted = True
                    return
            # Small sleep to avoid busy-waiting
            self._stop_listening.wait(0.05)

    def _listen_unix(self):
        """Unix-specific ESC detection using termios."""
        # Save terminal settings
        fd = sys.stdin.fileno()
        self._original_settings = termios.tcgetattr(fd)

        try:
            # Set terminal to raw mode for character-by-character input
            tty.setraw(fd)

            while not self._stop_listening.is_set():
                # Check if input is available (with timeout)
                ready, _, _ = select.select([sys.stdin], [], [], 0.05)

                if ready:
                    ch = sys.stdin.read(1)
                    # ESC key is '\x1b'
                    if ch == '\x1b':
                        self._interrupted = True
                        return
        finally:
            self._restore_terminal()

    def _restore_terminal(self):
        """Restore terminal settings on Unix."""
        if sys.platform != 'win32' and self._original_settings:
            try:
                fd = sys.stdin.fileno()
                termios.tcsetattr(fd, termios.TCSADRAIN, self._original_settings)
                self._original_settings = None
            except Exception:
                pass


# Global singleton instance
_interrupt_handler: Optional[InterruptHandler] = None


def get_interrupt_handler() -> InterruptHandler:
    """Get or create the global interrupt handler instance."""
    global _interrupt_handler
    if _interrupt_handler is None:
        _interrupt_handler = InterruptHandler()
    return _interrupt_handler


def is_interrupted() -> bool:
    """Convenience function to check if interrupted."""
    handler = get_interrupt_handler()
    return handler.is_interrupted()
