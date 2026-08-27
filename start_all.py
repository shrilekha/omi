"""
Starts all three OMI services (OMI itself, omi-deepdive, omi-benchmarks) with
one command, for local development. Before launching, creates any missing
.env from that service's .env.example (never touches one that already
exists) and installs each service's requirements.txt — so a fresh checkout
(or a Codespace after a requirements.txt change) is runnable with nothing
more than:

    python start_all.py

Each service's output is prefixed with its name so you can tell them apart
in one interleaved stream. Ctrl+C stops all three (and any Flask debug-mode
reloader child each one spawned) rather than leaving one running on its port.

This is a dev convenience, not a deployment tool — production still runs
each service separately behind its own gunicorn/Nginx (see each service's
own README).
"""
import os
import shutil
import signal
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
IS_WINDOWS = os.name == 'nt'

# (display name, app root — where .env/.env.example live, backend dir — where app.py runs from)
SERVICES = [
    ('OMI', ROOT, os.path.join(ROOT, 'backend')),
    ('omi-deepdive', os.path.join(ROOT, 'omi-deepdive'), os.path.join(ROOT, 'omi-deepdive', 'backend')),
    ('omi-benchmarks', os.path.join(ROOT, 'omi-benchmarks'), os.path.join(ROOT, 'omi-benchmarks', 'backend')),
]

# cyan / magenta / yellow — one per service, cycled if there were ever more
COLORS = ['\033[36m', '\033[35m', '\033[33m']
RESET = '\033[0m'
_print_lock = threading.Lock()


def ensure_env(name, app_root):
    env_path = os.path.join(app_root, '.env')
    example_path = env_path + '.example'
    if os.path.exists(env_path):
        print(f'[{name}] .env already exists — left untouched')
        return
    if not os.path.exists(example_path):
        print(f'[{name}] no .env.example found at {example_path} — skipping')
        return
    shutil.copy(example_path, env_path)
    print(f'[{name}] created .env from .env.example (edit it before relying on this for anything real)')


def install_requirements(name, backend_dir):
    """pip install -r requirements.txt for one service, using this same
    interpreter so it lands wherever `python app.py` will actually run from.
    Idempotent — pip no-ops quickly when everything's already satisfied, so
    this is cheap to run on every launch, not just the first."""
    req_path = os.path.join(backend_dir, 'requirements.txt')
    if not os.path.exists(req_path):
        return True
    print(f'[{name}] installing dependencies...')
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '-q', '-r', req_path],
        cwd=backend_dir,
    )
    if result.returncode != 0:
        print(f'[{name}] pip install failed (exit {result.returncode}) — not starting this service')
        return False
    return True


def stream_output(proc, name, color):
    for line in iter(proc.stdout.readline, ''):
        if not line:
            break
        with _print_lock:
            print(f'{color}[{name}]{RESET} {line.rstrip()}')


def start(name, backend_dir):
    popen_kwargs = {}
    if IS_WINDOWS:
        # Its own process group so Ctrl+C's CTRL_BREAK_EVENT (sent below) can
        # reach the Flask debug reloader's child process too, not just the
        # watcher we spawn directly — otherwise the reloader's worker can be
        # left running and squatting on the port after this script exits.
        popen_kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        popen_kwargs['start_new_session'] = True

    return subprocess.Popen(
        [sys.executable, 'app.py'],
        cwd=backend_dir,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1,
        **popen_kwargs,
    )


def stop(proc):
    if proc.poll() is not None:
        return
    try:
        if IS_WINDOWS:
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except Exception:
        proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if IS_WINDOWS:
            proc.kill()
        else:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception:
                proc.kill()


def main():
    print('Setting up .env files...\n')
    for name, app_root, _ in SERVICES:
        ensure_env(name, app_root)

    print('\nInstalling dependencies...\n')
    to_start = [
        (name, backend_dir) for name, _, backend_dir in SERVICES
        if install_requirements(name, backend_dir)
    ]
    if not to_start:
        print('\nNo services could be started — every pip install failed.')
        return

    print('\nStarting service(s) — Ctrl+C to stop all of them.\n')
    running = []
    for (name, backend_dir), color in zip(to_start, COLORS):
        proc = start(name, backend_dir)
        running.append((name, proc))
        threading.Thread(target=stream_output, args=(proc, name, color), daemon=True).start()

    def handle_term(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, handle_term)

    try:
        while True:
            for name, proc in running:
                code = proc.poll()
                if code is not None:
                    print(f'\n[{name}] exited (code {code}) — stopping the others.')
                    raise KeyboardInterrupt
            time.sleep(0.5)
    except KeyboardInterrupt:
        print('\nStopping all services...')
    finally:
        for _, proc in running:
            stop(proc)


if __name__ == '__main__':
    main()
