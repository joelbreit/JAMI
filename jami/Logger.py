# If you want, you can import verbose, save_output, and output_file from another file like:
# import Tools.Global_Variables as const

import re

from datetime import datetime


class Formats:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Logger:
    # When the Logger class is imported into another file, the start_time class variable is set.
    start_time = datetime.now()
    num_issues = 0
    verbose = False
    save_output = False
    output_file = 'output.txt'

    def _format_mode(mode):
        color = None
        if mode == 'DEBUG':
            color = Formats.OKCYAN
        elif mode == 'INFO':
            color = Formats.OKGREEN
        elif mode == 'WARN':
            color = Formats.WARNING
        elif mode == 'ERROR':
            color = Formats.FAIL
        elif mode == 'PROGR':
            color = Formats.OKBLUE
        mode = '{0: <8}'.format('[' + mode + '] ')
        return f'{color}' + mode + f'{Formats.END}'

    def _format(args, mode, delimiter=' '):
        delta_time = datetime.now() - Logger.start_time
        mode = Logger._format_mode(mode)
        output = ''.join(mode + str(delta_time)[0:10]) + ' - '
        for s in args:
            if isinstance(s, str):
                output += s
            else:
                output += str(s)
            output += delimiter
        return output

    def _output(args, mode, erase=False, delimiter=' '):
        output = Logger._format(
            args, mode=mode, delimiter=delimiter) + '                                '
        if erase:
            print(output, end="\r")
        else:
            print(output)
            file_output = re.sub(r'\033\[[0-9;]*m', '', output)
            file_output += '\n'
            if Logger.save_output:
                with open(Logger.output_file, 'a+') as log:
                    log.write(str(file_output))

    def info(*args, erase=False, delimiter=' '):
        Logger._output(args, mode='INFO', erase=erase, delimiter=delimiter)

    def debug(*args, erase=False, delimiter=' '):
        if Logger.verbose:
            Logger._output(args, mode='DEBUG', erase=erase,
                           delimiter=delimiter)

    def warn(*args, erase=False, delimiter=' '):
        Logger._output(args, mode='WARN', erase=erase, delimiter=delimiter)

    def error(*args, erase=False, delimiter=' '):
        Logger._output(args, mode='ERROR', erase=erase, delimiter=delimiter)

    def display_progress(title, interation, max, final=False):
        percent = interation/max
        progress_bar_width = 30
        filled = round(progress_bar_width*percent)
        space = progress_bar_width - filled
        output = title + '█'*filled + ' '*space + \
            str(round(percent*100)) + '%              '
        if final or percent == 1.0:
            Logger._output(output, mode='PROGR', delimiter='')
        else:
            Logger._output(output, mode='PROGR', erase=True, delimiter='')
