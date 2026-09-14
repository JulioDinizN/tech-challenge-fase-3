"""Recording-only SAST fixture; never imported or executed by the service."""
import subprocess


def demo_unsafe_command(command: str) -> None:
    subprocess.run(command, shell=True, check=True)
