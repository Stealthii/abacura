"""Temporary module with 'global' commands

Need until Mard's PluginManager is ready
"""
import re
import sys
from functools import partial

from rich.panel import Panel
from rich.pretty import Pretty

from abacura.mud import OutputMessage
from abacura.plugins import Plugin, command, action


class PluginDemo(Plugin):
    """Sample plugin to knock around"""
    def __init__(self):
        super().__init__()

    @command
    def foo(self) -> None:
        self.session.output(f"{sys.path}")
        self.session.output(f"{self.app.sessions}", markup=True)
        self.session.output(
            f"MSDP HEALTH: [bold red]🛜 [bold green]🛜  {self.session}", markup=True)

    @action("Ptam", flags=re.IGNORECASE)
    def ptam(self):
        self.session.output("PTAM!!", actionable=False)

    @action("spoon", flags=re.IGNORECASE)
    def spoon(self, msg: OutputMessage):
        msg.gag = True

    @action("Ptam (.*)")
    def ptam2(self, s: str):
        self.session.output(f"PTAM!! [{s}]")


class PluginCommandHelper(Plugin):
    """Display help for a command and evaluate a string"""

    def __init__(self):
        super().__init__()

    @command()
    def help(self):
        help_text = ["Plugin Commands", "\nUsage: @command <arguments>", "\nAvailable Commands: "]

        commands = [c for c in self.director.command_manager.commands if c.name != 'help']

        for c in sorted(commands, key=lambda c: c.name):
            doc = getattr(c.callback, '__doc__', None)
            doc = "" if doc is None else ": " + doc
            help_text.append(f"  {c.name:10s} {doc}")

        help_text.append("")
        self.session.output("\n".join(help_text))

    @command(name="?")
    def help_question(self):
        """Display list of commands"""
        self.help()

    @command
    def plugin(self) -> None:
        """Get information about plugins"""

        self.session.output("Current registered global plugins:")

        for plugin_name, plugin in self.session.plugin_loader.plugins.items():
            indicator = '[bold green]✓' if plugin.plugin_enabled else '[bold red]x'
            self.session.output(
                f"{indicator} [white]{plugin.get_name()}" +
                f" - {plugin.get_help()}", markup=True)

    @command
    def ticker(self, name: str, message: str = '', seconds: float = 0, repeats: int = -1, delete: bool = False):
        """Create/delete a ticker"""
        if not message:
            raise ValueError("Must specify a message")

        if seconds <= 0:
            raise ValueError("Seconds must be more than 0")

        # always remove an existing ticker with this name
        self.remove_ticker(name)
        if delete:
            return

        self.add_ticker(seconds=seconds, callback_fn=partial(self.session.output, msg=message),
                        repeats=repeats, name=name)

    @command(name="alias")
    def alias(self):
        """list, remove add aliases"""
        buf = "[bold white]Aliases:\n"
        for key in self.director.alias_manager.aliases.items():
            self.session.output(Pretty(key), actionable=False)
            buf += f"{key[0]}: {key[1]}\n"

        self.session.output(Panel(buf), actionable=False)


class PluginSession(Plugin):
    """Session specific commands"""
    @command(name="echo")
    def echo(self, text: str):
        """Send text to screen without triggering actions"""
        self.session.output(text, actionable=False)

    @command
    def showme(self, text: str) -> None:
        """Send text to screen as if it came from the socket, triggers actions"""
        self.session.output(text, markup=True)

    @command
    def msdp_command(self, variable: str = '') -> None:
        """Dump MSDP values for debugging"""
        if "REPORTABLE_VARIABLES" not in self.msdp.values:
            self.session.output("[bold red]# MSDPERROR: MSDP NOT LOADED?", markup=True)

        if not variable:
            panel = Panel(Pretty(self.msdp.values), highlight=True)
        else:
            panel = Panel(Pretty(self.msdp.values.get(variable, None)), highlight=True)
        self.session.output(panel, highlight=True, actionable=False)


class PluginMeta(Plugin):
    @command
    def meta(self) -> None:
        """Hyperlink demo"""
        self.session.output("Meta info blah blah")
        self.session.output("Obtained from https://kallisti.nonserviam.net/hero-calc/Pif")
