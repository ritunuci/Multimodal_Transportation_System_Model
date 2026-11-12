"""Run a script under an audit hook that logs file opens / fs mutations."""
import sys, os, runpy, time
script, log_path = os.path.abspath(sys.argv[1]), sys.argv[2]
_log = open(log_path, "w", buffering=1, encoding="utf-8")
_t0 = time.time()
SKIP_EXT = (".py", ".pyc", ".pyd", ".dll", ".so", ".pth")
SKIP_DIR = os.path.normcase(sys.prefix)
EVENTS = {"open", "os.mkdir", "os.remove", "os.rename", "os.rmdir", "os.truncate",
          "shutil.copyfile", "shutil.copytree", "shutil.rmtree", "shutil.move", "os.listdir", "os.scandir"}
_busy = False


def hook(event, args):
    global _busy
    if _busy or event not in EVENTS:
        return
    _busy = True
    try:
        if event == "open":
            path, mode, flags = args
            if not isinstance(path, (str, bytes, os.PathLike)):
                return
            path = os.fsdecode(path)
            if mode is None:  # os.open: derive from flags
                mode = "w" if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND) else "r"
            extra = mode
        else:
            path = os.fsdecode(args[0]) if args and isinstance(args[0], (str, bytes, os.PathLike)) else str(args)
            extra = ("-> " + os.fsdecode(args[1])) if event in ("os.rename", "shutil.copyfile", "shutil.copytree", "shutil.move") else ""
        ap = os.path.abspath(path)
        nc = os.path.normcase(ap)
        if nc.startswith(SKIP_DIR) or nc.endswith(SKIP_EXT) or "__pycache__" in nc:
            return
        _log.write(f"{time.time()-_t0:.2f}\t{event}\t{extra}\t{ap}\n")
    except Exception:
        pass
    finally:
        _busy = False


sys.addaudithook(hook)
sys.argv = [script]
sys.path.insert(0, os.path.dirname(script))
runpy.run_path(script, run_name="__main__")
