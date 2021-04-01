"""Module provides logging functionality."""
from logging import NOTSET, Handler, Logger


class RPLogger(Logger):
    """RPLogger class for logging tests."""

    def __init__(self, name, level=NOTSET):
        """
        Initialize RPLogger instance.

        :param name:  logger name
        :param level: level of logs
        """
        super().__init__(name, level=level)

    def _log(
        self,
        level,
        msg,
        args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
        file_to_attach=None,
        is_launch_log=False,
    ):
        if file_to_attach or is_launch_log:
            extra = extra or {}
            if file_to_attach:
                extra["file_to_attach"] = file_to_attach
            if is_launch_log:
                extra["is_launch_log"] = is_launch_log
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)

    def makeRecord(
        self,
        name,
        level,
        fn,
        lno,
        msg,
        args,
        exc_info,
        func=None,
        extra=None,
        sinfo=None,
    ):
        """Override building of record to add custom fields."""
        record = super().makeRecord(
            name, level, fn, lno, msg, args, exc_info, func, extra, sinfo
        )

        record.is_launch_log = False
        record.file_to_attach = None
        if extra:
            record.file_to_attach = extra.get("file_to_attach", None)
            record.is_launch_log = extra.get("is_launch_log", False)

        return record


class RPHandler(Handler):
    """Provide ability to send logs to Report Portal."""

    def __init__(self, rp, level=NOTSET):
        """Initialize handler."""
        super().__init__(level)
        self.rp = rp

    def emit(self, record):
        """Send log message to Report Portal."""
        msg = self.format(record)
        if record.is_launch_log:
            self.rp.post_launch_log(
                msg, record.levelname, file_to_attach=record.file_to_attach
            )
        else:
            self.rp.post_log(
                msg, record.levelname, file_to_attach=record.file_to_attach
            )
