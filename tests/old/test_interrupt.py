"""
Tests for interrupt handler functionality.
"""

import pytest
import time
import threading
from agents.pulsus.console.interrupt_handler import InterruptHandler, get_interrupt_handler


class TestInterruptHandler:
    """Test interrupt handler functionality."""

    def test_initialization(self):
        """Test handler initializes correctly."""
        handler = InterruptHandler()
        assert handler.is_interrupted() is False

    def test_reset(self):
        """Test reset clears interrupt flag."""
        handler = InterruptHandler()
        handler._interrupted = True
        handler.reset()
        assert handler.is_interrupted() is False

    def test_singleton_pattern(self):
        """Test get_interrupt_handler returns same instance."""
        handler1 = get_interrupt_handler()
        handler2 = get_interrupt_handler()
        assert handler1 is handler2

    def test_manual_interrupt(self):
        """Test manually setting interrupt flag."""
        handler = InterruptHandler()
        handler._interrupted = True
        assert handler.is_interrupted() is True

    def test_start_stop_listening(self):
        """Test start and stop listening."""
        handler = InterruptHandler()

        # Start listening
        handler.start_listening()
        assert handler._listener_thread is not None

        # Give thread time to start
        time.sleep(0.1)

        # Stop listening
        handler.stop_listening()

        # Wait for thread to finish
        time.sleep(0.2)

        # Should have cleaned up
        assert handler._stop_listening.is_set()


class TestInterruptIntegration:
    """Integration tests for interrupt functionality."""

    def test_interrupt_during_long_operation(self):
        """Test interrupt can stop a long-running operation."""
        handler = InterruptHandler()
        handler.reset()

        results = {"completed": False, "iterations": 0}

        def long_operation():
            """Simulate long operation that checks for interrupts."""
            for i in range(100):
                if handler.is_interrupted():
                    results["iterations"] = i
                    return
                time.sleep(0.01)  # Simulate work

            results["completed"] = True
            results["iterations"] = 100

        # Start the operation in a thread
        op_thread = threading.Thread(target=long_operation)
        op_thread.start()

        # Simulate interrupt after short delay
        time.sleep(0.05)
        handler._interrupted = True

        # Wait for operation to finish
        op_thread.join(timeout=2.0)

        # Should have interrupted before completion
        assert results["completed"] is False
        assert results["iterations"] < 100

    def test_no_interrupt_completes_normally(self):
        """Test operation completes when no interrupt occurs."""
        handler = InterruptHandler()
        handler.reset()

        results = {"completed": False}

        def short_operation():
            """Simulate short operation."""
            for i in range(10):
                if handler.is_interrupted():
                    return
                time.sleep(0.01)

            results["completed"] = True

        op_thread = threading.Thread(target=short_operation)
        op_thread.start()
        op_thread.join(timeout=2.0)

        # Should have completed normally
        assert results["completed"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
