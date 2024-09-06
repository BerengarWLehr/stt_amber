#!/bin/env python3

from time import sleep
from amber_script import AmberScript


KEY_FILE = '/home/ber/Projekte/NextcloudAssistantSttAmber/secret.key'
AUDIO_FILE = '/home/ber/Video/Wird der technische Fortschritt uns vor dem Klimawandel retten - Nein.mp3'


def main():
    with open(KEY_FILE, 'r', encoding='utf8') as key_file:
        amber_script = AmberScript(key_file.read())
    # print("Scheduling transcription")
    # job_id = amber_script.transcribe(AUDIO_FILE)
    job_id = '66dad7086eb0395cc59603f1'
    print("Checking status")
    while not amber_script.done(job_id):
        print("Waiting 1sec")
        sleep(1)
    print("Fetching data")
    print(amber_script.fetch(job_id))


if __name__ == "__main__":
    main()
