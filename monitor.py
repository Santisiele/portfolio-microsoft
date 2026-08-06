import sys
import time
import psutil


def find_app_process():
    for p in psutil.process_iter(["name", "cmdline"]):
        cmd = " ".join(p.info["cmdline"] or [])
        if "app.py" in cmd and "python" in (p.info["name"] or "").lower():
            return p
    return None


def get_target():
    if len(sys.argv) > 1:
        return psutil.Process(int(sys.argv[1]))
    p = find_app_process()
    if p is None:
        sys.exit("Could not find the app.py process. Pass a PID: python monitor.py <PID>")
    return p


def process_tree(proc):
    procs = [proc]
    try:
        procs += proc.children(recursive=True)
    except psutil.Error:
        pass
    return procs


def main():
    target = get_target()
    print(f"Monitoring PID {target.pid}  —  Ctrl+C to quit\n")

    for p in process_tree(target):
        try:
            p.cpu_percent(None)
        except psutil.Error:
            pass

    ncpu = psutil.cpu_count() or 1
    total_ram_mb = psutil.virtual_memory().total / (1024 ** 2)

    try:
        while True:
            time.sleep(1)
            procs = process_tree(target)
            cpu = rss = 0.0
            threads = 0
            for p in procs:
                try:
                    cpu += p.cpu_percent(None)
                    rss += p.memory_info().rss / (1024 ** 2)
                    threads += p.num_threads()
                except psutil.Error:
                    pass
            print(
                f"\rCPU: {cpu:6.1f}%  ({cpu / ncpu:5.1f}% of total) | "
                f"RAM: {rss:8.1f} MB ({rss / total_ram_mb * 100:4.1f}%) | "
                f"threads: {threads:3d} | processes: {len(procs)}    ",
                end="", flush=True,
            )
    except KeyboardInterrupt:
        print("\nDone.")
    except psutil.NoSuchProcess:
        print("\nProcess ended.")


if __name__ == "__main__":
    main()