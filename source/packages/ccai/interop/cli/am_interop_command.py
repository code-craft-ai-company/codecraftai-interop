#!/usr/bin/env python3
"""
.. module:: am_interop_command
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The script entrypoint for the 'am-interop' command.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


import os

import click


from ccai.xmodules.fspath import get_package_paths
from ccai.xmodules.ximport import import_by_name


def discover_command_groups(root: click.Group):
    """
        Discovers command sub-packages under ``ccai.interop.cli.cmdtree`` and registers
        their command groups onto the provided root group.

        :param root: The root :class:`click.Group` that discovered groups attach to.
    """
    import ccai.interop.cli.cmdtree

    for nxtpath in get_package_paths(ccai.interop.cli.cmdtree):
        for child_name in os.listdir(nxtpath):
            child_dir_full = os.path.join(nxtpath, child_name)

            # Only consider sub-packages (directories) that expose an 'xinit' module.
            # This skips non-package entries like README.md and the package __init__,
            # which previously caused an import-time ModuleNotFoundError.
            if not os.path.isdir(child_dir_full):
                continue

            xinit_file = os.path.join(child_dir_full, "xinit.py")
            if not os.path.exists(xinit_file):
                continue

            cmd_reg_modname = f"ccai.interop.cli.cmdtree.{child_name}.xinit"
            init_mod = import_by_name(cmd_reg_modname)
            if hasattr(init_mod, 'register_groups'):
                init_mod.register_groups(root)

    return


@click.group("am-interop")
@click.option('-v', '--verbose', count=True)
def am_interop_root_command(verbose):

    from ccai.runtime.activation import activate_runtime, ActivationProfile
    from ccai.runtime.optionoverrides import AM_RUNTIME_OPTION_OVERRIDES

    if verbose == 0:
        console_level = "WARNING"
    elif verbose == 1:
        console_level = "INFO"
    elif verbose == 2:
        console_level = "DEBUG"
    else:
        console_level = "NOTSET"

    # Activate the runtime for a console application, then apply the verbosity
    # override to the console log level.
    activate_runtime(profile=ActivationProfile.Console)
    AM_RUNTIME_OPTION_OVERRIDES.override_loglevel_console(console_level)

    return


discover_command_groups(am_interop_root_command)


if __name__ == '__main__':
    am_interop_root_command()
