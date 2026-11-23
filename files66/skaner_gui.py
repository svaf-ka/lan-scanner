#!/usr/bin/env python3
"""
LAN Scanner - aplikacja z okienkiem.
Pokazuje urządzenia podłączone do Twojej sieci lokalnej (IP, nazwa, MAC).
Nie wymaga instalowania żadnych bibliotek.
Skanuj tylko własną sieć albo taką, do której masz zgodę.
"""

import ipaddress
import platform
import queue
import re
import socket
import subprocess
import threading
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import ttk

IS_WINDOWS = platform.system() == "Windows"
NO_WINDOW = subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0
MAC_RE = re.compile(r"([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

# Kolory
BG = "#0b1220"
PANEL = "#111a2e"
ROW_ALT = "#0e1627"
HEADER = "#16223a"
TEXT = "#e5e7eb"
MUTED = "#94a3b8"
ACCENT = "#22d3ee"
ACCENT_HOVER = "#67e8f9"
GREEN = "#a7f3d0"

ICON_B64 = "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"


def run(cmd, timeout=5):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          stdin=subprocess.DEVNULL, creationflags=NO_WINDOW)


def ping(ip):
    if IS_WINDOWS:
        cmd = ["ping", "-n", "1", "-w", "700", ip]
    else:
        cmd = ["ping", "-c", "1", "-W", "1", ip]
    try:
        return run(cmd, 4).returncode == 0
    except Exception:
        return False


def read_arp_table():
    outputs = []
    if not IS_WINDOWS:
        try:
            outputs.append(run(["ip", "neigh"]).stdout)
        except Exception:
            pass
    try:
        outputs.append(run(["arp", "-a"]).stdout)
    except Exception:
        pass
    table = {}
    for out in outputs:
        for line in out.splitlines():
            ip, mac = IP_RE.search(line), MAC_RE.search(line)
            if ip and mac:
                m = mac.group(0).replace("-", ":").upper()
                if m != "FF:FF:FF:FF:FF:FF":
                    table[ip.group(0)] = m
    return table


def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return "-"


def my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return ""
    finally:
        s.close()


def get_gateway():
    """Próbuje sam znaleźć IP routera."""
    try:
        if IS_WINDOWS:
            out = run(["route", "print", "-4", "0.0.0.0"]).stdout
            best = None
            for line in out.splitlines():
                p = line.split()
                if len(p) >= 5 and p[0] == "0.0.0.0" and p[1] == "0.0.0.0":
                    try:
                        metric = int(p[4])
                    except ValueError:
                        continue
                    if best is None or metric < best[0]:
                        best = (metric, p[2])
            if best and IP_RE.fullmatch(best[1]):
                return best[1]
        else:
            out = run(["ip", "route"]).stdout
            m = re.search(r"default via (\d+\.\d+\.\d+\.\d+)", out)
            if m:
                return m.group(1)
    except Exception:
        pass
    ip = my_ip()
    if ip:
        return ip.rsplit(".", 1)[0] + ".1"
    return "192.168.1.1"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LAN Scanner")
        self.configure(bg=BG)
        self.minsize(720, 420)
        self.q = queue.Queue()
        self.row_count = 0

        w, h = 880, 580
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        try:
            self.icon_img = tk.PhotoImage(data=ICON_B64)
            self.iconphoto(True, self.icon_img)
            self.logo_img = self.icon_img.subsample(2, 2)
        except Exception:
            self.logo_img = None

        self.setup_style()
        self.build_ui()
        self.dark_titlebar()
        self.after(100, self.poll)

    # ---------- wygląd ----------
    def setup_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", background=BG, foreground=TEXT, fieldbackground=PANEL,
                    font=("Segoe UI", 10), borderwidth=0)
        s.configure("TFrame", background=BG)
        s.configure("TLabel", background=BG, foreground=TEXT)
        s.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground=ACCENT)
        s.configure("Sub.TLabel", foreground=MUTED)
        s.configure("Status.TLabel", foreground=MUTED, padding=(0, 4))

        s.configure("TEntry", fieldbackground=PANEL, foreground=TEXT, insertcolor=TEXT,
                    bordercolor=HEADER, lightcolor=HEADER, darkcolor=HEADER, padding=6)
        s.map("TEntry", bordercolor=[("focus", ACCENT)], lightcolor=[("focus", ACCENT)],
              darkcolor=[("focus", ACCENT)])

        s.configure("Accent.TButton", background=ACCENT, foreground="#06202a",
                    font=("Segoe UI", 10, "bold"), padding=(20, 7), borderwidth=0,
                    focusthickness=0, focuscolor=ACCENT)
        s.map("Accent.TButton",
              background=[("disabled", "#334155"), ("active", ACCENT_HOVER)],
              foreground=[("disabled", MUTED)])

        s.configure("Horizontal.TProgressbar", troughcolor=PANEL, background=ACCENT,
                    bordercolor=BG, lightcolor=ACCENT, darkcolor=ACCENT, thickness=6)

        s.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT,
                    rowheight=32, borderwidth=0, font=("Segoe UI", 10))
        s.map("Treeview", background=[("selected", "#164e63")],
              foreground=[("selected", "#ffffff")])
        s.configure("Treeview.Heading", background=HEADER, foreground=ACCENT,
                    font=("Segoe UI", 10, "bold"), relief="flat", padding=(8, 8))
        s.map("Treeview.Heading", background=[("active", "#1e2d4d")])

        s.configure("Vertical.TScrollbar", background="#1e293b", troughcolor=BG,
                    bordercolor=BG, arrowcolor=MUTED, lightcolor="#1e293b",
                    darkcolor="#1e293b")
        s.map("Vertical.TScrollbar", background=[("active", "#334155")])

    def build_ui(self):
        # nagłówek
        header = ttk.Frame(self, padding=(20, 18, 20, 6))
        header.pack(fill="x")
        if self.logo_img:
            ttk.Label(header, image=self.logo_img).pack(side="left", padx=(0, 12))
        titles = ttk.Frame(header)
        titles.pack(side="left")
        ttk.Label(titles, text="LAN Scanner", style="Title.TLabel").pack(anchor="w")
        ttk.Label(titles, text="Urządzenia w Twojej sieci lokalnej",
                  style="Sub.TLabel").pack(anchor="w")

        # sterowanie
        controls = ttk.Frame(self, padding=(20, 10, 20, 10))
        controls.pack(fill="x")
        ttk.Label(controls, text="IP routera").pack(side="left")
        self.ip_var = tk.StringVar(value=get_gateway())
        entry = ttk.Entry(controls, textvariable=self.ip_var, width=18)
        entry.pack(side="left", padx=10)
        entry.bind("<Return>", lambda e: self.start())
        self.btn = ttk.Button(controls, text="Skanuj", style="Accent.TButton",
                              command=self.start, cursor="hand2")
        self.btn.pack(side="left")

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill="x", padx=20, pady=(0, 10))

        # tabela
        frame = ttk.Frame(self, padding=(20, 0, 20, 0))
        frame.pack(fill="both", expand=True)
        cols = ("ip", "name", "mac", "note")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col, title, width, stretch in (("ip", "Adres IP", 140, False),
                                           ("name", "Nazwa", 300, True),
                                           ("mac", "MAC", 170, False),
                                           ("note", "Opis", 130, False)):
            self.tree.heading(col, text=title, anchor="w")
            self.tree.column(col, width=width, anchor="w", stretch=stretch)
        self.tree.tag_configure("even", background=PANEL)
        self.tree.tag_configure("odd", background=ROW_ALT)
        self.tree.tag_configure("router", foreground=ACCENT_HOVER)
        self.tree.tag_configure("me", foreground=GREEN)
        self.tree.bind("<Double-1>", self.copy_ip)

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # pasek statusu
        bar = ttk.Frame(self, padding=(20, 6, 20, 10))
        bar.pack(fill="x")
        self.status = tk.StringVar(value="Gotowy. Kliknij „Skanuj”.")
        ttk.Label(bar, textvariable=self.status, style="Status.TLabel").pack(side="left")
        ttk.Label(bar, text="Kliknij dwukrotnie wiersz, aby skopiować IP",
                  style="Status.TLabel").pack(side="right")

    def dark_titlebar(self):
        """Ciemny pasek tytułu na Windows 10/11 (jeśli system pozwala)."""
        if not IS_WINDOWS:
            return
        try:
            import ctypes
            self.update()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            value = ctypes.c_int(1)
            for attr in (20, 19):
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, attr, ctypes.byref(value), ctypes.sizeof(value))
        except Exception:
            pass

    # ---------- działanie ----------
    def copy_ip(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        ip = self.tree.item(item, "values")[0]
        self.clipboard_clear()
        self.clipboard_append(ip)
        self.status.set(f"Skopiowano {ip}")

    def start(self):
        router = self.ip_var.get().strip()
        try:
            ipaddress.IPv4Address(router)
        except ValueError:
            self.status.set("To nie wygląda na poprawny adres IP.")
            return
        self.tree.delete(*self.tree.get_children())
        self.row_count = 0
        self.progress["value"] = 0
        self.btn.state(["disabled"])
        self.status.set("Skanuję...")
        threading.Thread(target=self.worker, args=(router,), daemon=True).start()

    def worker(self, router):
        try:
            network = ipaddress.ip_network(f"{router}/24", strict=False)
            hosts = [str(h) for h in network.hosts()]
            total = len(hosts)
            done = 0
            with ThreadPoolExecutor(max_workers=100) as pool:
                for _ in pool.map(ping, hosts):
                    done += 1
                    if done % 5 == 0 or done == total:
                        self.q.put(("progress", done, total))

            arp = read_arp_table()
            me = my_ip()
            found = {ip: mac for ip, mac in arp.items()
                     if ipaddress.IPv4Address(ip) in network}
            if me and me not in found:
                found[me] = "-"
            ips = sorted(found, key=lambda x: ipaddress.IPv4Address(x))

            count = 0
            with ThreadPoolExecutor(max_workers=30) as pool:
                for ip, name in zip(ips, pool.map(get_hostname, ips)):
                    note = "router" if ip == router else ("ten komputer" if ip == me else "")
                    self.q.put(("row", ip, name, found[ip], note))
                    count += 1
            self.q.put(("done", count))
        except Exception as e:
            self.q.put(("error", str(e)))

    def poll(self):
        try:
            while True:
                msg = self.q.get_nowait()
                kind = msg[0]
                if kind == "progress":
                    self.progress["maximum"] = msg[2]
                    self.progress["value"] = msg[1]
                elif kind == "row":
                    ip, name, mac, note = msg[1:]
                    tags = ["even" if self.row_count % 2 == 0 else "odd"]
                    if note == "router":
                        tags.append("router")
                    elif note == "ten komputer":
                        tags.append("me")
                    self.tree.insert("", "end", values=(ip, name, mac, note), tags=tags)
                    self.row_count += 1
                elif kind == "done":
                    self.status.set(f"Gotowe. Znaleziono urządzeń: {msg[1]}")
                    self.btn.state(["!disabled"])
                elif kind == "error":
                    self.status.set(f"Błąd: {msg[1]}")
                    self.btn.state(["!disabled"])
        except queue.Empty:
            pass
        self.after(100, self.poll)


if __name__ == "__main__":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # ostry tekst na Windowsie
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("lan.scanner.app")
    except Exception:
        pass
    App().mainloop()
