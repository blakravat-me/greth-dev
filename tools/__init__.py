"""Tool per agen; mengimpor paket ini mendaftarkan semua tool ke registry di policy.py."""

from importlib import import_module

for _name in ("add_strategy", "mission_completed", "evaluate", "internet_search", "read_url", "write_note"):
    import_module(f"tools.{_name}.tool")
