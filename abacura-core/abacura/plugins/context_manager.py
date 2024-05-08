class ContextError(Exception):
    pass


class PluginContextManager:
    _session_contexts: dict[str, dict] = {}
    current_context: dict | None = None

    def __init__(self, session_name: str = "", **kwargs) -> None:
        self.previous_context: dict | None = None
        self.session_name = session_name
        PluginContextManager._session_contexts[session_name] = kwargs.copy()

    def __enter__(self):
        self.previous_context = self.current_context
        PluginContextManager.current_context = self._session_contexts.setdefault(self.session_name, {})
        print("enter")

    def __exit__(self, exception_type, exception_value, exception_traceback):
        PluginContextManager.current_context = self.previous_context
        print("exit")

    @classmethod
    def inject(cls, session_name: str, inject_name: str, obj: object, overwrite: bool = False) -> None:
        session_context = cls._session_contexts.setdefault(session_name, {})

        if inject_name in session_context and not overwrite:
            raise ValueError(f"Session [{session_name}] context already contains [{inject_name}]")

        session_context[inject_name] = obj

    @classmethod
    def remove_session(cls, session_name: str) -> None:
        cls._session_contexts.pop(session_name)


class Plugin:
    def __init__(self, n: int) -> None:
        print(n)

    def __new__(cls, context: dict):
        instance = super().__new__(cls)
        instance._context = context
        print("context", context)

        # if "context" in kwargs:
        #     instance._context = kwargs["context"]
        # elif PluginContextManager.current_context:
        #     instance._context = PluginContextManager.current_context
        # elif getattr(instance, "_context", None) is None:
        #     raise ContextError("Unable to determine context")

        return instance

    @property
    def world(self) -> str:
        return self._context["world"]

    @property
    def session(self) -> str:
        return self._context["session"]
