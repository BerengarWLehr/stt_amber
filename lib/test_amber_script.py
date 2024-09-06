#!/usr/bin/env python3

from time import sleep
from amber_script import AmberScript


KEY_FILE = '/home/ber/Projekte/NextcloudAssistantSttAmber/secret.key'
AUDIO_FILE = '/home/ber/Lehrcloud/misc/Jean-Claude Juncker - ich sitze \
quietsch fidel auf meinem Bett und rede mit Ihnen (DLF 2019-03-20).mp3'


def main():
    with open(KEY_FILE, 'r', encoding='utf8') as key_file:
        amber_script = AmberScript(key_file.read())
    print("Scheduling transcription")
    job_id = amber_script.transcribe(AUDIO_FILE)
    print("Checking status")
    while not amber_script.done(job_id):
        print("Waiting 10sec")
        sleep(10)
    print("Fetching data")
    print(amber_script.fetch(job_id))


if __name__ == "__main__":
    main()
