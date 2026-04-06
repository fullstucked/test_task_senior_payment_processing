class BaseApplicationError(Exception):
    """
    Base class for all application-specific errors.
    """

    def __init__(self, message: str, context: dict | None = None):
        super().__init__(message)
        self.context = context or {}

    def __repr__(self) -> str:
        if not self.context:
            return f"{self.__class__.__name__}('{self.args[0]}')"
        ctx = ', '.join(f'{k}={v!r}' for k, v in self.context.items())
        return f"{self.__class__.__name__}('{self.args[0]}', context={{ {ctx} }})"

    @property
    def detail(self) -> str:
        return 'An application error occurred'


class RetryableError(BaseApplicationError):
    pass


class NonRetryableError(BaseApplicationError):
    pass
