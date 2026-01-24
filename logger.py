import logging

dbg = logging.getLogger()

# pretty satisfying log format colors from https://github.com/KamilMatejuk/Articles/blob/main/Inside%20Python/01.%20Colorful%20logging/loggers.py
class AnsiColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        no_style = '\033[0m'
        bold = '\033[91m'
        grey = '\033[90m'
        yellow = '\033[93m'
        red = '\033[31m'
        red_light = '\033[91m'
        start_style = {
            'DEBUG': grey,
            'INFO': no_style,
            'WARNING': yellow,
            'ERROR': red,
            'CRITICAL': red_light + bold,
        }.get(record.levelname, no_style)
        end_style = no_style
        return f'{start_style}{super().format(record)}{end_style}'

_handler = logging.StreamHandler()
_handler.setLevel(logging.DEBUG)
_formatter = AnsiColorFormatter('{asctime} | {levelname:<8s} | {message}', style='{')
_handler.setFormatter(_formatter)
dbg.addHandler(_handler)
dbg.setLevel(logging.DEBUG)
