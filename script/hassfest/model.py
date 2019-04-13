"""Models for manifest validator."""
import json
from typing import List, Dict, Any
import pathlib

import attr


@attr.s
class Error:
    """Error validating an integration."""

    plugin = attr.ib(type=str)
    error = attr.ib(type=str)
    fixable = attr.ib(type=bool, default=False)

    def __str__(self) -> str:
        """Reprepsentat error as string."""
        return "[{}] {}".format(self.plugin.upper(), self.error)


@attr.s
class Config:
    """Config for the run."""

    root = attr.ib(type=pathlib.Path)
    action = attr.ib(type=str)
    errors = attr.ib(type=List[Error], factory=list)
    cache = attr.ib(type=Dict[str, Any], factory=dict)

    def add_error(self, *args, **kwargs):
        """Add an error."""
        self.errors.append(Error(*args, **kwargs))


@attr.s
class Integration:
    """Represent an integration in our validator."""

    @classmethod
    def load_dir(cls, path: pathlib.Path):
        """Load all integrations in a directory."""
        assert path.is_dir()
        integrations = {}
        for fil in path.iterdir():
            if fil.is_file() or fil.name == '__pycache__':
                continue

            integration = cls(fil)
            integration.load_manifest()
            integrations[integration.domain] = integration

        return integrations

    path = attr.ib(type=pathlib.Path)
    manifest = attr.ib(type=dict, default=None)
    errors = attr.ib(type=List[Error], factory=list)

    @property
    def domain(self) -> str:
        """Integration domain."""
        return self.path.name

    @property
    def manifest_path(self) -> pathlib.Path:
        """Integration manifest path."""
        return self.path / 'manifest.json'

    def add_error(self, *args, **kwargs):
        """Add an error."""
        self.errors.append(Error(*args, **kwargs))

    def load_manifest(self) -> None:
        """Load manifest."""
        if not self.manifest_path.is_file():
            self.add_error(
                'model',
                "Manifest file {} not found".format(self.manifest_path)
            )
            return

        try:
            manifest = json.loads(self.manifest_path.read_text())
        except ValueError as err:
            self.add_error(
                'model',
                "Manifest contains invalid JSON: {}".format(err)
            )
            return

        self.manifest = manifest