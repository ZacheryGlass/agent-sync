from nicegui import ui, app
import sys
import threading
import queue
from pathlib import Path
from typing import Optional

from core.registry import FormatRegistry
from core.orchestrator import UniversalSyncOrchestrator, FilePair
from core.state_manager import SyncStateManager
from core.canonical_models import ConfigType
from adapters import ClaudeAdapter, CopilotAdapter

CONFIG_TYPE_MAP = {
    'Agent': ConfigType.AGENT,
    'Permission': ConfigType.PERMISSION,
    'Prompt': ConfigType.PROMPT
}

class SyncApp:
    def __init__(self):
        self.log_queue = queue.Queue()
        self.conflict_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # UI Elements (to be initialized in setup_ui)
        self.source_dir = None
        self.target_dir = None
        self.source_format = None
        self.target_format = None
        self.config_type = None
        self.direction = None
        self.check_force = None
        self.check_verbose = None
        self.check_hint = None
        self.check_handoffs = None
        self.log_area = None
        self.conflict_dialog = None
        self.conflict_details = None

    def setup_ui(self):
        with ui.header().classes('bg-primary text-white'):
            ui.label('Coding Agent Settings Sync').classes('text-h6')

        with ui.column().classes('w-full p-4 gap-4'):
            # Directory Selection
            with ui.card().classes('w-full'):
                ui.label('Directories').classes('text-lg font-bold')
                with ui.row().classes('w-full items-center'):
                    self.source_dir = ui.input('Source Directory').classes('flex-grow')
                    ui.button(icon='folder', on_click=lambda: self.pick_dir(self.source_dir))
                
                with ui.row().classes('w-full items-center'):
                    self.target_dir = ui.input('Target Directory').classes('flex-grow')
                    ui.button(icon='folder', on_click=lambda: self.pick_dir(self.target_dir))

            # Configuration
            with ui.card().classes('w-full'):
                ui.label('Configuration').classes('text-lg font-bold')
                with ui.row().classes('w-full gap-4'):
                    self.source_format = ui.select(['claude', 'copilot'], label='Source Format', value='claude').classes('w-1/4')
                    self.target_format = ui.select(['claude', 'copilot'], label='Target Format', value='copilot').classes('w-1/4')
                    self.config_type = ui.select(list(CONFIG_TYPE_MAP.keys()), label='Config Type', value='Agent').classes('w-1/4')
                    self.direction = ui.select(['both', 'source-to-target', 'target-to-source'], label='Direction', value='both').classes('w-1/4')

                with ui.row().classes('w-full gap-4'):
                    self.check_force = ui.checkbox('Force (Auto-resolve conflicts)')
                    self.check_verbose = ui.checkbox('Verbose Logging', value=True)
                    self.check_hint = ui.checkbox('Add Argument Hint (Copilot)')
                    self.check_handoffs = ui.checkbox('Add Handoffs (Copilot)')

            # Actions
            with ui.row().classes('w-full gap-4'):
                ui.button('Dry Run', icon='preview', on_click=lambda: self.run_sync(dry_run=True)).classes('bg-secondary text-white')
                ui.button('Sync', icon='sync', on_click=lambda: self.run_sync(dry_run=False)).classes('bg-primary text-white')

            # Logs
            with ui.card().classes('w-full'):
                ui.label('Logs').classes('text-lg font-bold')
                self.log_area = ui.log().classes('w-full h-64 font-mono bg-gray-100 p-2 rounded')

        # Conflict Dialog
        self.conflict_dialog = ui.dialog()
        with self.conflict_dialog, ui.card():
            ui.label('Conflict Detected').classes('text-h6 text-red-600')
            self.conflict_details = ui.markdown()
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Use Source', on_click=lambda: self.resolve_conflict('source_to_target'))
                ui.button('Use Target', on_click=lambda: self.resolve_conflict('target_to_source'))
                ui.button('Skip', on_click=lambda: self.resolve_conflict(None)).classes('bg-gray-500')

        # Start timers
        ui.timer(0.1, self.process_logs)
        ui.timer(0.1, self.process_conflicts)

    async def pick_dir(self, input_element):
        path = input_element.value or '.'
        result = await LocalFilePicker(directory=path, show_hidden_files=True)
        if result:
            input_element.set_value(result[0])

    def logger_callback(self, msg=""):
        self.log_queue.put(str(msg))

    def conflict_resolver_callback(self, pair: FilePair):
        self.conflict_queue.put(pair)
        return self.response_queue.get()

    def process_logs(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_area.push(msg)

    def process_conflicts(self):
        if not self.conflict_queue.empty():
            pair = self.conflict_queue.get()
            self.show_conflict_dialog(pair)

    def show_conflict_dialog(self, pair: FilePair):
        details = f"**File:** `{pair.base_name}`\n\n* **Source:** `{pair.source_path}`\n* **Target:** `{pair.target_path}`"
        self.conflict_details.set_content(details)
        self.conflict_dialog.open()

    def resolve_conflict(self, action):
        self.conflict_dialog.close()
        self.response_queue.put(action)

    def run_sync(self, dry_run=False):
        if not self.source_dir.value or not self.target_dir.value:
            ui.notify('Please specify source and target directories.', type='negative')
            return
        self.log_area.clear()
        threading.Thread(target=self._sync_logic, args=(dry_run,), daemon=True).start()

    def _sync_logic(self, dry_run):
        try:
            source_dir = Path(self.source_dir.value).expanduser().resolve()
            target_dir = Path(self.target_dir.value).expanduser().resolve()
            if not source_dir.exists():
                self.logger_callback(f"Error: Source directory does not exist: {source_dir}")
                return

            registry = FormatRegistry()
            registry.register(ClaudeAdapter())
            registry.register(CopilotAdapter())
            state_manager = SyncStateManager()

            conversion_options = {}
            if self.check_hint.value: conversion_options['add_argument_hint'] = True
            if self.check_handoffs.value: conversion_options['add_handoffs'] = True

            orchestrator = UniversalSyncOrchestrator(
                source_dir=source_dir, target_dir=target_dir,
                source_format=self.source_format.value, target_format=self.target_format.value,
                config_type=CONFIG_TYPE_MAP[self.config_type.value],
                format_registry=registry, state_manager=state_manager,
                direction=self.direction.value, dry_run=dry_run,
                force=self.check_force.value, verbose=self.check_verbose.value,
                conversion_options=conversion_options,
                logger=self.logger_callback, conflict_resolver=self.conflict_resolver_callback
            )
            orchestrator.sync()
            self.logger_callback("Dry run completed." if dry_run else "Sync completed.")
        except Exception as e:
            self.logger_callback(f"Error: {e}")

class LocalFilePicker(ui.dialog):
    def __init__(self, directory: str, show_hidden_files: bool = False):
        super().__init__()
        self.path = Path(directory).expanduser()
        if not self.path.exists(): self.path = Path('.')
        self.show_hidden_files = show_hidden_files
        with self, ui.card():
            self.grid = ui.aggrid({
                'columnDefs': [{'field': 'name', 'headerName': 'File', 'sortable': True}],
                'rowSelection': 'single',
            }, html_columns=[0]).classes('w-96').on('cellDoubleClicked', self.handle_double_click)
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=self.close).props('outline')
                ui.button('Ok', on_click=self._handle_ok)
        self.update_grid()

    def update_grid(self):
        paths = list(self.path.glob('*'))
        if not self.show_hidden_files: paths = [p for p in paths if not p.name.startswith('.')] # noqa: E713
        paths.sort(key=lambda p: (not p.is_dir(), p.name.lower()))
        rows = []
        if self.path.parent != self.path:
            rows.append({'name': '📁 ..', 'path': str(self.path.parent), 'is_dir': True})
        for p in paths:
            if p.is_dir(): rows.append({'name': f'📁 {p.name}', 'path': str(p), 'is_dir': True})
        self.grid.options['rowData'] = rows
        self.grid.update()

    def handle_double_click(self, e):
        if e.args['data']['is_dir']:
            self.path = Path(e.args['data']['path'])
            self.update_grid()

    def _handle_ok(self):
        self.submit([str(self.path)])

# Use a decorator to explicitly define the root page
@ui.page('/')
def main_page():
    app_instance = SyncApp()
    app_instance.setup_ui()

def start():
    # reload=False is critical to avoid re-running the script in complex entry points
    ui.run(title='Coding Agent Settings Sync', reload=False, port=8080, show=False)

if __name__ in {"__main__", "__mp_main__"}:
    start()