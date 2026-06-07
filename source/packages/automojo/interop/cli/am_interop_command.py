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


import os

import click


from automojo.xmodules.fspath import get_package_paths
from automojo.xmodules.ximport import import_by_name


def discover_command_groups(root: click.Group):
    """
        Discovers modules under the namespace package 'automojo.interop.cli.cmdtree' and

    """
    import automojo.interop.cli.cmdtree

    first_found = set()

    for nxtpath in get_package_paths(automojo.interop.cli.cmdtree):
        for child_name in os.listdir(nxtpath):
            child_dir_full = os.path.join(nxtpath, child_name)
            child_init = os.path.join(child_dir_full)
            
            if os.path.exists(child_init):
                child_mod_full = f"automojo.interop.cli.cmdtree.{child_name}"
                cmd_reg_modname = f"{child_mod_full}.xinit"
                init_mod = import_by_name(cmd_reg_modname)
                if hasattr(init_mod, 'register_groups'):
                    init_mod.register_groups(root)

    return


@click.group("am-interop")
@click.option('-v', '--verbose', count=True)
def am_interop_root_command(verbose):

    from automojo.thisapp.runtimevariables import AM_RUNTIME_VARIABLES

    
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


discover_command_groups(am_interop_root_command)


if __name__ == '__main__':
    am_interop_root_command()
