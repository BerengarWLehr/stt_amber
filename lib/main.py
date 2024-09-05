"""Tha main module of the llm2 app
"""

import threading
import tempfile
import time
import typing
from contextlib import asynccontextmanager
import os

from fastapi import Depends, FastAPI, UploadFile
from nc_py_api import AsyncNextcloudApp, NextcloudApp
from nc_py_api.ex_app import anc_app, run_app, set_handlers
from amber_script import AmberScript


UPDATE_INTERVAL = 10
amber_script = AmberScript("A", "0")
task_ids = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    set_handlers(app, enabled_handler)
    yield

APP = FastAPI(lifespan=lifespan)


def push_to_amberscript(file_path, nc_task_id):
    as_task_id = amber_script.transcribe(file_path)
    task_ids[as_task_id] = nc_task_id
    update_process = threading.Thread(target=check_for_done, args=[as_task_id])
    update_process.start()


def check_for_done(as_task_id: int):
    while not amber_script.done(as_task_id):
        time.sleep(UPDATE_INTERVAL)
    NextcloudApp().providers.speech_to_text.report_result(
        task_ids[as_task_id],
        amber_script.fetch(as_task_id))


@APP.post("/amberscript")
async def add_transcription(
    _nc: typing.Annotated[AsyncNextcloudApp, Depends(anc_app)],
    data: UploadFile,
    task_id: int,
):
    if data.filename is None:
        return
    _, file_extension = os.path.splitext(data.filename)
    task_file = tempfile.NamedTemporaryFile(mode="w+b", suffix=f"{file_extension}")
    task_file.write(await data.read())
    push_to_amberscript(task_file, task_id)


async def enabled_handler(enabled: bool, nc: AsyncNextcloudApp) -> str:
    print(f"enabled={enabled}")
    if enabled is True:
        await nc.providers.speech_to_text.register(
            'stt_amberscript',
            'AmberScript',
            '/amberscript')
    else:
        await nc.providers.speech_to_text.unregister(
            'stt_amberscript')
    return ""


if __name__ == "__main__":
    run_app("main:APP", log_level="trace")
