from __future__ import annotations

from abacura.plugins.task_queue import Task


class SpellTask(Task):
    def insert_check(self) -> bool:
        return self.msdp.position in ["Standing", "Fighting", "Flying", "Mounted"]


class NCOSpellTask(Task):
    def insert_check(self) -> bool:
        return self.msdp.position in ["Standing", "Flying", "Mounted"]
