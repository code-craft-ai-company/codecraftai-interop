"""
    Command-tree package for the ``am-interop`` CLI.

    Extension distributions contribute their own command groups by shipping a
    ``ccai/interop/cli/cmdtree/<group>/xinit.py`` of their own. When those
    distributions are not installed into the same directory as this one (an
    editable checkout beside an installed wheel, for example), a plain package
    would only ever see its own directory. Extending ``__path__`` merges every
    ``cmdtree`` directory found on ``sys.path`` so discovery sees them all.
"""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)
