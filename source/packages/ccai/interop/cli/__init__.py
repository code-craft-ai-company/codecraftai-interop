

# Extension distributions ship their own ``ccai/interop/cli/cmdtree/<group>`` directories; merging
# every ``cli`` directory on sys.path here is what lets the ``cmdtree`` package below merge theirs.
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
