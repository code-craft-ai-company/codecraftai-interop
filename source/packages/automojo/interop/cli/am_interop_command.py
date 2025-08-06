#!/usr/bin/env python3
"""
.. module:: am_interop_command
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The script entrypoint for the 'am-interop' command.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import click

from automojo.interop.cli.cmdtree.upnp import group_am_interop_upnp


@click.group("am-interop")
@click.option('-v', '--verbose', count=True)
def am_interop_root_command(verbose):

    from automojo.runtime.runtimevariables import AM_RUNTIME_VARIABLES

    
    if verbose == 0:
        AM_RUNTIME_VARIABLES.AM_LOG_LEVEL_CONSOLE = "WARNING"
    elif verbose == 1:
        AM_RUNTIME_VARIABLES.AM_LOG_LEVEL_CONSOLE = "INFO"
    elif verbose == 2:
        AM_RUNTIME_VARIABLES.AM_LOG_LEVEL_CONSOLE = "DEBUG"
    elif verbose > 2:
        AM_RUNTIME_VARIABLES.AM_LOG_LEVEL_CONSOLE = "NOTSET"

    from automojo.runtime.initialize import initialize_runtime
    initialize_runtime()

    return


am_interop_root_command.add_command(group_am_interop_upnp)


if __name__ == '__main__':
    am_interop_root_command()
