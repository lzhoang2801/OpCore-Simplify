import sys
import subprocess
import shlex
import os

class SecureRun:
    def __init__(self,
                 allowed_cmds=None,
                 allowed_args=None,
                 safe_cwd=None,
                 safe_env=None,
                 max_output_bytes=10 * 1024 * 1024,  # 10MB
                 default_timeout=300  # 5 minutes
                 ):
        # Whitelist of command names (no paths unless inside safe_cwd)
        self.allowed_cmds = set(allowed_cmds or [
            "ls", "cp", "mv", "mkdir", "rm", "echo", "cat"
        ])
        # Optional simple arg whitelist (per command customize as needed)
        self.allowed_args = allowed_args or {}
        # Constrain working dir
        self.safe_cwd = os.path.abspath(safe_cwd) if safe_cwd else None
        # Minimal environment
        self.safe_env = safe_env or {
            "PATH": "/usr/bin:/bin",
            "LANG": "C",
            "LC_ALL": "C"
        }
        self.max_output_bytes = max_output_bytes
        self.default_timeout = default_timeout

    def _sanitize_args(self, args):
        if isinstance(args, str):
            parsed = shlex.split(args, posix=True)
        elif isinstance(args, list):
            parsed = list(args)
        else:
            raise ValueError("Arguments must be a list or string")

        if not parsed:
            raise ValueError("Empty command")

        cmd = parsed[0]
        # Reject absolute paths unless inside safe_cwd
        if os.path.isabs(cmd):
            if not self.safe_cwd or not os.path.commonpath([self.safe_cwd, os.path.abspath(cmd)]) == self.safe_cwd:
                raise PermissionError(f"Absolute command path not allowed: {cmd}")
            cmd_name = os.path.basename(cmd)
        else:
            cmd_name = cmd

        if cmd_name not in self.allowed_cmds and cmd_name != "sudo":
            raise PermissionError(f"Command not allowed: {cmd_name}")

        # Basic argument whitelist per command (optional)
        allowed = self.allowed_args.get(cmd_name)
        if allowed:
            for a in parsed[1:]:
                if a.startswith("-") and a not in allowed:
                    raise PermissionError(f"Flag not allowed for {cmd_name}: {a}")

        # Reject common shell metacharacters
        for a in parsed:
            if any(m in a for m in ["|", "&", ";", ">", "<", "$(", "`"]):
                raise PermissionError(f"Shell metacharacter not allowed in arg: {a}")

        return parsed

    def _popen(self, args, cwd=None, env=None):
        return subprocess.Popen(
            args,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
            universal_newlines=False,
            close_fds=("posix" in sys.builtin_module_names),
            cwd=cwd or self.safe_cwd,
            env=env or self.safe_env
        )

    def run(self, command,
            timeout=None,
            print_stdout=False,
            print_stderr=False,
            allow_sudo=False):
        args = self._sanitize_args(command)

        # Warn if sudo is used
        if args[0] == "sudo" or allow_sudo:
            print("⚠️ Warning: sudo usage may introduce privilege escalation risks if running commands that you don't know what they do.")

        p = self._popen(args)

        to = timeout if timeout is not None else self.default_timeout
        try:
            stdout_bytes, stderr_bytes = p.communicate(timeout=to)
        except subprocess.TimeoutExpired:
            p.kill()
            stdout_bytes, stderr_bytes = p.communicate()
            return "", "Timeout expired", 124
        except Exception as e:
            try:
                p.kill()
            except Exception:
                pass
            return "", f"Execution error: {e}", 1

        if len(stdout_bytes) > self.max_output_bytes:
            stdout_bytes = stdout_bytes[:self.max_output_bytes]
        if len(stderr_bytes) > self.max_output_bytes:
            stderr_bytes = stderr_bytes[:self.max_output_bytes]

        def decode_clean(b):
            s = b.decode("utf-8", errors="replace")
            return "".join(ch for ch in s if ch.isprintable() or ch in "\n\r\t")

        stdout = decode_clean(stdout_bytes)
        stderr = decode_clean(stderr_bytes)

        if print_stdout and stdout:
            print(stdout)
        if print_stderr and stderr:
            print(stderr)

        return stdout, stderr, p.returncode
