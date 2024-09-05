"""Tha amber_script connector for the stt nextcloud app
"""

import requests

# See https://amberscript.github.io/api-docs

class AmberScript:
    AMBERSCRIPT_URL='https://qs.amberscript.com'

    def __init__(self, api_token: str):
        self.api_token = api_token

    def transcribe(self, file_path: str) -> int:
        with open(file_path, 'rb') as file_content
            response = requests.post(
                f'{self.AMBERSCRIPT_URL}/jobs/upload-media',
                data=file_content,
                params={
                    'apiKey': self.api_token,
                    'language': 'auto',
                    'direct': 'perfect',
                    'numberOfSpeakers': 0}, timeout=100).json()
        return response['jobId']

    def done(self, job_id: int) -> bool:
        response = requests.get(f'{self.AMBERSCRIPT_URL}/jobs/status', params={
            'apiKey': self.api_token,
            'jobId': job_id},
            timeout=100).json()
        status = response['jobStatus']['status']
        if status == 'ERROR':
            raise Exception(f'job {job_id} ended with error')
        return status == 'DONE'

    def fetch(self, job_id: int, format: str = 'srt') -> str:
        if format not in ['srt', 'vtt', 'txt', 'json']:
            raise Exception('Invalid export format')
        response = requests.get(f'{self.AMBERSCRIPT_URL}/jobs/export-{format}', params={
            'apiKey': self.api_token,
            'jobId': job_id}, timeout=100).json()
        file_url = response.downloadUrl
        return requests.get(file_url).text
