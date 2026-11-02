import os
import signal
import sys
import threading
import traceback


def install_sigusr1_handler():
    """
    Install a SIGUSR1 handler that prints the stack of all threads,
    to help debug hangs in the HTTP app or the importer.
    """
    signal.signal(signal.SIGUSR1, _sigusr1_handler)


def _sigusr1_handler(signal_number, frame):  # pragma: no cover
    thread_names = {th.ident: th.name for th in threading.enumerate()}
    code = [f"Traceback follows for all threads of process {os.getpid()}:"]
    for thread_id, stack in sys._current_frames().items():
        thread_name = thread_names.get(thread_id, "")
        code.append(f"\n## Thread: {thread_name}({thread_id}) ##\n")
        code += traceback.format_list(traceback.extract_stack(stack))
    print("".join(code))
