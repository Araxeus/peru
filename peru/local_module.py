import os

from . import compat
from . import resolver


class LocalModule:
    def __init__(self, imports, default_rule, path, peru_dir=None):
        self.imports = imports
        self.default_rule = default_rule
        self.path = path

        # The toplevel module might relocate its own .peru directory with the
        # PERU_DIR variable. Overridden remote modules will just use the
        # default.
        # NOTE: You can get into a confusing situation if you use a nonstandard
        # .peru dir in your project, and then also use your project as a local
        # override for a *different* project. The two different perus won't be
        # talking to the same lastimports file, and your imports may get dirty.
        # This is a tiny corner case, but maybe we should try to detect it?
        self.peru_dir = peru_dir or os.path.join(path, ".peru")
        compat.makedirs(self.peru_dir)

    def apply_imports(self, runtime):
        last_imports_tree_path = os.path.join(self.peru_dir, 'lastimports')
        last_imports_tree = None
        if os.path.exists(last_imports_tree_path):
            with open(last_imports_tree_path) as f:
                last_imports_tree = f.read()

        unified_imports_tree = resolver.apply_imports(
            runtime, self.imports, self.path, last_imports_tree)

        if unified_imports_tree:
            with open(last_imports_tree_path, 'w') as f:
                f.write(unified_imports_tree)
        elif os.path.exists(last_imports_tree_path):
            os.remove(last_imports_tree_path)

    def do_build(self, runtime, rules):
        """Runs all the build rules, taking their export paths into account.
        Returns the final export path."""
        self.apply_imports(runtime)
        path = self.path
        if self.default_rule:
            path = self.default_rule.do_build(path)
        for rule in rules:
            path = rule.do_build(path)
        return path
