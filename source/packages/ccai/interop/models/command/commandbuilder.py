"""
    .. module:: builder
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing command builder for constructing and executing 
               commands through ISystemContext agents.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import Optional, Dict

import shlex

# Import dependencies from ccai packages
from ccai.interop.aspects import AspectsCmd, DEFAULT_CMD_ASPECTS, ActionPattern, LoggingPattern
from ccai.interop.interfaces.isystemcontext import ISystemContext

# Import CommandResult from models module
from ccai.interop.models.command.commandresult import CommandResult


def _replace_cmd_aspects(base: AspectsCmd, **overrides) -> AspectsCmd:
    """
        Builds a new :class:`AspectsCmd` from an existing one with selected fields
        overridden. ``AspectsCmd`` is a :class:`Freezable` (immutable, not a dataclass),
        so ``dataclasses.replace`` cannot be used; this reconstructs the instance from
        its current field values plus the overrides.

        :param base: The :class:`AspectsCmd` whose values seed the new instance.
        :param overrides: Field values to override on the new instance.

        :returns: A new frozen :class:`AspectsCmd`.
    """
    kwargs = {
        "expected_status": base.expected_status,
        "user": base.user,
        "pty_params": base.pty_params,
        "action_pattern": base.action_pattern,
        "completion_timeout": base.completion_timeout,
        "completion_interval": base.completion_interval,
        "connection_timeout": base.connection_timeout,
        "connection_interval": base.connection_interval,
        "inactivity_timeout": base.inactivity_timeout,
        "inactivity_interval": base.inactivity_interval,
        "monitor_delay": base.monitor_delay,
        "logging_pattern": base.logging_pattern,
        "retry_logging_interval": base.retry_logging_interval,
        "allowed_error_codes": base.allowed_error_codes,
        "allowed_connection_exceptions": base.allowed_connection_exceptions,
    }
    kwargs.update(overrides)
    rtnval = AspectsCmd(**kwargs)
    return rtnval


class CommandBuilder:
    """
        Fluent interface for building and executing commands through ISystemContext agents.
        
        Provides methods for configuring command execution context including elevation,
        environment variables, working directory, and execution aspects, then executing
        the command directly through LocalCommandAgent or SshAgent.
    """
    
    def __init__(self, args: list[str], aspects: AspectsCmd = DEFAULT_CMD_ASPECTS):
        """
            Initialize CommandBuilder with command arguments.
            
            :param args: Command arguments list (e.g., ["ls", "-la"])
            :param aspects: Command execution behavior aspects.
        """
        self._args = args.copy()
        self._elevated = False
        self._cwd: Optional[str] = None
        self._env: Optional[Dict[str, str]] = None
        self._aspects = aspects
        self._sudo_path = "/usr/bin/sudo"
        self._dry_run = False
        return

    @classmethod
    def command(cls, args: list[str]) -> "CommandBuilder":
        """
            Convenience function to create a CommandBuilder instance.
            
            :param args: Command arguments list
            
            :returns: New CommandBuilder instance
        """
        return cls(args)

    def elevated(self, sudo_path: str = "/usr/bin/sudo") -> "CommandBuilder":
        """
            Configure command to run with elevated privileges (sudo).
            
            :param sudo_path: Path to sudo executable
            
            :returns: Self for method chaining
        """
        self._elevated = True
        self._sudo_path = sudo_path
        return self
    
    def with_env(self, env: Dict[str, str]) -> "CommandBuilder":
        """
            Configure environment variables for command execution.
            
            :param env: Dictionary of environment variables
            
            :returns: Self for method chaining
        """
        if self._env is None:
            self._env = {}
        self._env.update(env)
        return self
    
    def in_directory(self, cwd: str) -> "CommandBuilder":
        """
            Configure working directory for command execution.
            
            :param cwd: Working directory path
            
            :returns: Self for method chaining
        """
        self._cwd = cwd
        return self
    
    def with_aspects(self, aspects: AspectsCmd) -> "CommandBuilder":
        """
            Configure execution aspects for retry, timeout, and logging behavior.
            
            :param aspects: AspectsCmd instance controlling execution behavior
            
            :returns: Self for method chaining
        """
        self._aspects = aspects
        return self
    
    def with_timeout(self, timeout_seconds: float) -> "CommandBuilder":
        """
            Configure command timeout using completion_timeout in aspects.
            
            This method creates a new AspectsCmd based on the current aspects
            but with the specified completion_timeout value.
            
            :param timeout_seconds: Timeout in seconds for command completion
            
            :returns: Self for method chaining
        """
        # Create new aspects with updated timeout
        base = DEFAULT_CMD_ASPECTS if self._aspects is None else self._aspects
        self._aspects = _replace_cmd_aspects(base, completion_timeout=timeout_seconds)
        return self
    
    def with_retry(self, action_pattern: ActionPattern) -> "CommandBuilder":
        """
            Configure retry behavior through ActionPattern in aspects.
            
            This method creates a new AspectsCmd based on the current aspects
            but with the specified ActionPattern for retry behavior.
            
            :param action_pattern: ActionPattern controlling retry behavior
            
            :returns: Self for method chaining
        """
        # Create new aspects with updated action pattern
        base = DEFAULT_CMD_ASPECTS if self._aspects is None else self._aspects
        self._aspects = _replace_cmd_aspects(base, action_pattern=action_pattern)
        return self
    
    def with_logging(self, logging_pattern: LoggingPattern) -> "CommandBuilder":
        """
            Configure logging behavior through LoggingPattern in aspects.
            
            This method creates a new AspectsCmd based on the current aspects
            but with the specified LoggingPattern for logging behavior.
            
            :param logging_pattern: LoggingPattern controlling logging behavior
            
            :returns: Self for method chaining
        """
        # Create new aspects with updated logging pattern
        base = DEFAULT_CMD_ASPECTS if self._aspects is None else self._aspects
        self._aspects = _replace_cmd_aspects(base, logging_pattern=logging_pattern)
        return self
    
    def dry_run(self, enabled: bool = True) -> "CommandBuilder":
        """
            Configure dry-run mode for command execution.
            
            When dry-run is enabled, commands return synthetic success results
            without actually executing through the agent.
            
            :param enabled: Whether to enable dry-run mode
            
            :returns: Self for method chaining
        """
        self._dry_run = enabled
        return self
    
    def build_command(self) -> str:
        """
            Build the complete shell command string with all context.
            
            Constructs a shell command that handles:
            - Environment variable exports
            - Working directory changes  
            - Privilege elevation via sudo
            - Proper shell escaping
            
            :returns: Complete shell command string ready for execution
        """
        parts = []
        
        # Environment variables - export each one
        if self._env:
            for key, value in self._env.items():
                parts.append(f"export {key}={shlex.quote(value)}")
        
        # Working directory change
        if self._cwd:
            parts.append(f"cd {shlex.quote(self._cwd)}")
        
        # Build the actual command with optional elevation
        command_args = self._args.copy()
        if self._elevated:
            command_args = [self._sudo_path, "-n"] + command_args
        
        # Add the command with proper shell escaping - each arg individually quoted
        command_str = " ".join(shlex.quote(arg) for arg in command_args)
        parts.append(command_str)
        
        # Join all parts with && to ensure proper execution order
        # If only command (no env or cwd), return just the command
        if len(parts) == 1:
            return parts[0]
        else:
            return " && ".join(parts)
    
    def execute(self, agent: ISystemContext) -> CommandResult:
        """
            Execute the built command through the provided ISystemContext agent.
            
            Ensures that aspects are properly configured and passed to the agent
            for timeout, retry, and logging behavior control. Tracks execution 
            duration and timeout status.
            
            :param agent: ISystemContext agent (LocalCommandAgent or SshAgent)
            
            :returns: CommandResult with execution details and output
        """
        import time
        
        # Build the complete command string
        command = self.build_command()

        # In dry-run mode, return a synthetic success result without executing.
        if self._dry_run:
            transport = self._determine_transport(agent)
            rtnval = CommandResult(
                exit_code=0,
                stdout="",
                stderr="",
                command=self._args,
                transport=transport,
                duration_ms=0.0,
                timed_out=False,
                dry_run=True
            )
            return rtnval

        # Ensure aspects are properly configured
        aspects_to_use = self._aspects
        if aspects_to_use is None:
            # Fallback to default aspects if none configured
            aspects_to_use = DEFAULT_CMD_ASPECTS
        
        # Track execution time
        start_time = time.time()
        timed_out = False
        
        try:
            # Execute command through the agent with aspects
            # The aspects parameter controls:
            # - completion_timeout: timeout behavior
            # - action_pattern: retry behavior  
            # - logging_pattern: logging behavior
            status, stdout, stderr = agent.run_cmd(command, aspects=aspects_to_use)
        except Exception as e:
            # Check if this was a timeout exception
            # Different agents may raise different timeout exceptions
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                timed_out = True
                status = 124  # Standard timeout exit code
                stdout = ""
                stderr = f"Command timed out: {e}"
            else:
                # Re-raise non-timeout exceptions
                raise
        
        # Calculate duration
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000.0
        
        # Determine transport type based on agent type
        transport = self._determine_transport(agent)
        
        # Return consistent result format
        return CommandResult(
            exit_code=status,
            stdout=stdout,
            stderr=stderr,
            command=self._args,
            transport=transport,
            duration_ms=duration_ms,
            timed_out=timed_out
        )
    
    def _determine_transport(self, agent: ISystemContext) -> str:
        """
            Determine transport type based on agent class name.
            
            :param agent: ISystemContext agent
            
            :returns: Transport type ("local" or "ssh")
        """
        agent_class_name = agent.__class__.__name__
        if "ssh" in agent_class_name.lower():
            return "ssh"
        else:
            return "local"

    