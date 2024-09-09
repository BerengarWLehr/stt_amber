"""Simplest example of files_dropdown_menu + notification."""

import threading
import tempfile
import time
from typing import Annotated
from contextlib import asynccontextmanager
from os import path

from fastapi import Depends, FastAPI, responses
from nc_py_api import FsNode, AsyncNextcloudApp, NextcloudApp
from nc_py_api.ex_app import AppAPIAuthMiddleware, LogLvl, nc_app, run_app, set_handlers
from nc_py_api.files import ActionFileInfoEx
from amber_script import AmberScript

# See https://cloud-py-api.github.io/nc_py_api/NextcloudApp.html
# also https://cloud-py-api.github.io/app_api/notes_for_developers/ExAppOverview.html

UPDATE_INTERVAL = 10
KEY_FILE = 'secret.key'
FORMAT = 'srt'
# task_ids: dict[int, int] = {}
with open(KEY_FILE, 'r', encoding='utf8') as key_file:
    amber_script = AmberScript(key_file.read())


@asynccontextmanager
async def lifespan(app: FastAPI):
    set_handlers(app, enabled_handler)
    yield

APP = FastAPI(lifespan=lifespan)
APP.add_middleware(AppAPIAuthMiddleware)


def check_for_done(as_task_id: int, in_path: str, save_path: str, nc: NextcloudApp):
    try:
        while not amber_script.done(as_task_id):
            time.sleep(UPDATE_INTERVAL)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf8', suffix=f'.{FORMAT}') as tmp_out:
            tmp_out.write(amber_script.fetch(as_task_id, FORMAT))
            nc.log(LogLvl.WARNING, 'Transcription is ready')
            nc.files.upload_stream(save_path, tmp_out)
            nc.log(LogLvl.WARNING, 'Result uploaded')
            nc.notifications.create(f'{in_path} finished!', f'{save_path} is waiting for you!')
    except Exception as e:
        nc.log(LogLvl.ERROR, str(e))
        nc.notifications.create('Error occurred', 'Error information was written to log file')


def push_to_amberscript(input_file: FsNode, nc: NextcloudApp):
    save_path = path.splitext(input_file.user_path)[0] + '.' + FORMAT
    nc.log(LogLvl.WARNING, f"Processing:{input_file.user_path} -> {save_path}")
    with tempfile.NamedTemporaryFile(mode="w+b") as tmp_in:
        nc.files.download2stream(input_file, tmp_in)
        nc.log(LogLvl.WARNING, "File downloaded")
        tmp_in.flush()
        as_task_id = amber_script.transcribe(tmp_in.name)
    # task_ids[as_task_id] = (nc, save_path)
    update_process = threading.Thread(
        target=check_for_done,
        args=[as_task_id, input_file.name, save_path, nc])
    update_process.start()


@APP.post("/amberscript")
async def add_transcription(
    files: ActionFileInfoEx,
    nc: Annotated[NextcloudApp, Depends(nc_app)]
):
    for task_file in files.files:
        push_to_amberscript(task_file.to_fs_node(), nc)
    return responses.Response()


async def enabled_handler(enabled: bool, nc: AsyncNextcloudApp) -> str:
    print(f"enabled={enabled}")
    try:
        if enabled:
            await nc.ui.files_dropdown_menu.register_ex(
                'stt_amberscript',
                'Transcribe',
                '/amberscript',
                mime='audio'
            )
        else:
            await nc.ui.files_dropdown_menu.unregister(
                'stt_amberscript')
    except Exception as e:
        return str(e)
    return ''


if __name__ == '__main__':
    run_app('main:APP', log_level='trace')
