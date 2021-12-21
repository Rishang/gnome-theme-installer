import logging
import subprocess
import sys
from dataclasses import dataclass
from typing import List

# from . import exc
# from ._compat import MutableMapping, console_to_str, str_from_console

logger = logging.getLogger(__name__)


@dataclass
class ShellOutputs:
    stdout: List[str]
    stderr: List[str]
    returncode: int


class Shell:

    line_breaks = "\n"
    popen_args = {"shell": True, "stdout": subprocess.PIPE, "stderr": subprocess.PIPE}

    def console_to_str(self, s):
        console_encoding = sys.__stdout__.encoding

        """ From pypa/pip project, pip.backwardwardcompat. License MIT. """
        if s is None:
            return
        try:
            return s.decode(console_encoding, "ignore")
        except UnicodeDecodeError:
            return s.decode("utf_8", "ignore")

    def str_from_console(self, s):
        text_type = str

        try:
            return text_type(s)
        except UnicodeDecodeError:
            return text_type(s, encoding="utf_8")

    def cmd(self, cmd):
        try:
            process = subprocess.Popen(cmd, **self.popen_args)
            stdout, stderr = process.communicate()
            returncode = process.returncode

        except Exception as e:
            logger.error("Exception for %s: \n%s" % (subprocess.list2cmdline(cmd), e))

        returncode = returncode

        stdout = self.console_to_str(stdout)
        stdout = stdout.split(self.line_breaks)
        stdout = list(filter(None, stdout))  # filter empty values

        stderr = self.console_to_str(stderr)
        stderr = stderr.split(self.line_breaks)
        stderr = list(filter(None, stderr))  # filter empty values

        if "has-session" in cmd and len(stderr):
            if not stdout:
                stdout = stderr[0]

        logger.debug("stdout for %s: \n%s" % (" ".join(cmd), stdout))

        return ShellOutputs(stdout=stdout, stderr=stderr, returncode=returncode)


def sh(command: str, sudo: bool = False) -> ShellOutputs:
    s = Shell()
    return s.cmd(command)
