"""Tha amber_script connector for the stt nextcloud app
"""

from typing import IO, Any
import requests

# See https://amberscript.github.io/api-docs


class AmberScript:
    AMBERSCRIPT_URL = 'https://api.amberscript.com/api'

    def __init__(self, api_token: str):
        self.api_token = api_token

    def request(self,
                method: str,
                endpoint: str,
                params: dict[str, int | str] | None = None,
                *,
                job_id: int | None = None,
                file: IO | None = None) -> requests.Response:
        parameter = {
            'apiKey': self.api_token,
            **({} if job_id is None else {'jobId': job_id}),
            **({} if params is None else params)}
        response = requests.request(
            method=method,
            url=f'{self.AMBERSCRIPT_URL}/{endpoint}',
            files=None if file is None else {'file': file},
            params=parameter,
            timeout=100)
        if response.status_code != 200:
            raise Exception(response.text)
        return response

    def data(self, response: requests.Response) -> dict[str, Any]:
        response_data = response.json()
        if 'message' in response_data:
            raise Exception(response_data['message'])
        if 'error' in response_data:
            raise Exception(response_data['message'])
        return response_data

    def transcribe(self, file_path: str) -> int:
        with open(file_path, 'rb') as file:
            params: dict[str, int | str] = {
                'language': 'auto',
                'direct': 'perfect',
                'numberOfSpeakers': 0}
            response = self.data(self.request('POST', 'jobs/upload-media', params, file=file))
            return response['jobStatus']['jobId']

    def done(self, job_id: int) -> bool:
        response = self.data(self.request('GET', 'jobs/status', job_id=job_id))
        status = response['jobStatus']['status']
        if status == 'ERROR':
            raise Exception(f'job {job_id} ended with error')
        return status == 'DONE'

    def fetch(self, job_id: int, frmt: str = 'srt') -> str:
        return self.request('GET', f'jobs/export-{frmt}', job_id=job_id).text
