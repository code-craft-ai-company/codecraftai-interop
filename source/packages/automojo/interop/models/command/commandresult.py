"""
    .. module:: models
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing data models for command execution results.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import Optional

from dataclasses import dataclass

@dataclass
class CommandResult:
    """
        Result of a command execution through the command builder.
        
        Provides consistent result format regardless of which ISystemContext agent (LocalCommandAgent
        or SshAgent) was used for execution.
        
        This model satisfies Requirement 8: Consistent Result Format by ensuring that command results
        are consistently formatted from both LocalCommandAgent and SshAgent, allowing features to
        work identically regardless of which agent is used.
    """
    exit_code: int
    stdout: str
    stderr: str
    command: list[str]
    timed_out: bool = False
    dry_run: bool = False
    duration_ms: Optional[float] = None
    transport: str = "local"  # "local" or "ssh"
    
    def __post_init__(self):
        """
            Validate the CommandResult after initialization.
            
            Ensures that transport is one of the expected values and that
            duration_ms is non-negative if provided.
        """
        if self.transport not in ("local", "ssh"):
            raise ValueError(f"Invalid transport '{self.transport}'. Must be 'local' or 'ssh'.")
        
        if self.duration_ms is not None and self.duration_ms < 0:
            raise ValueError(f"Duration must be non-negative, got {self.duration_ms}")
    
    @property
    def succeeded(self) -> bool:
        """
            Check if the command execution was successful.
            
            :returns: True if exit_code is 0 and command did not time out
        """
        return self.exit_code == 0 and not self.timed_out
    
    @property
    def failed(self) -> bool:
        """
            Check if the command execution failed.
            
            :returns: True if exit_code is non-zero or command timed out
        """
        return not self.succeeded
    
    def __str__(self) -> str:
        """
            String representation of the command result.
            
            :returns: Human-readable summary of the execution result
        """
        status = "SUCCESS" if self.succeeded else "FAILED"
        duration_str = f" ({self.duration_ms:.1f}ms)" if self.duration_ms is not None else ""
        timeout_str = " [TIMEOUT]" if self.timed_out else ""
        dry_run_str = " [DRY-RUN]" if self.dry_run else ""
        
        return f"CommandResult[{status}] exit_code={self.exit_code} transport={self.transport}{duration_str}{timeout_str}{dry_run_str}"