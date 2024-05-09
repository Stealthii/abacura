from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import tomlkit


@dataclass
class Location:
    category: str
    name: str
    vnum: str
    temporary: bool = False


class LocationList:
    def __init__(self, loc_file: Path | str) -> None:
        if isinstance(loc_file, str):
            loc_file = Path(loc_file)
        self.locations: list[Location] = []
        self.loc_filepath = loc_file

        self.load()

    def save(self) -> None:
        toml_structure = {}
        for c in self.get_categories():
            toml_structure[c] = {loc.name: loc.vnum for loc in self.get_category(c) if not loc.temporary}

        with self.loc_filepath.open("w") as f:
            tomlkit.dump(toml_structure, f)

    def load(self) -> None:
        if not self.loc_filepath.exists():
            self.loc_filepath.parent.mkdir(parents=True, exist_ok=True)
            self.loc_filepath.touch()

        with self.loc_filepath.open() as f:
            toml_structure = tomlkit.load(f)
            locations: list[Location] = []
            for c in toml_structure:
                locations += [Location(c, k, v) for k, v in toml_structure[c].items()]

            self.locations = locations

    def get_locations_for_vnum(self, vnum: str) -> list[Location]:
        return [a for a in self.locations if a.vnum == vnum]

    @staticmethod
    def parse_location(location: str) -> tuple[str, str | None]:
        s = location.split(".")
        name = s[1] if len(s) > 1 else s[0]
        category = s[0] if len(s) > 1 else None

        return name, category

    def get_location(self, location: str) -> Location | None:
        name, category = self.parse_location(location)
        for a in self.locations:
            if a.name == name and (a.category == category or category is None):
                return a

        return None

    def add_location(self, location: str, vnum: str, temporary: bool = False) -> None:
        name, category = self.parse_location(location)

        if self.get_location(location) is None:
            self.locations.append(Location(category, name, vnum, temporary))
            self.save()

    def delete_location(self, location: str) -> None:
        existing_location = self.get_location(location)
        self.locations = [loc for loc in self.locations if loc != existing_location]
        self.save()

    def get_categories(self) -> Counter:
        return Counter([a.category for a in self.locations])

    def get_category(self, category: str) -> list[Location]:
        return [loc for loc in self.locations if loc.category.lower() == category.lower()]
