import os
import json
import logging
import requests
import sys
import warnings
import urllib3
from tonic_configuration import TonicConfiguration

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Suppress insecure request warnings due to self-signed certificate
warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

class TonicSession:
    def __init__(self, base_url, api_key):
        self._base_url = base_url
        self._session = requests.Session()
        self._session.verify = False  # Disable SSL certificate verification
        self._api_key = api_key
        self._api_version = "v2023.07.0"
        self._session.headers.update({"Authorization": f"Apikey {api_key}"})
        self.values_to_set = {  # Configuration defaults
            # List all configuration keys here with default values as empty strings or appropriate structures
        }

    def _get_url(self, api_snippet):
        return f"{self._base_url}{api_snippet}"

    def get_configuration(self, workspace_id, srcOrDest='src'):
        configuration_url = self._get_url("/api/DataSource")
        logging.debug(f'Calling: {configuration_url}')
        params = {"workspaceId": workspace_id, "api-version": self._api_version}
        response = self._session.get(configuration_url, params=params)
        response.raise_for_status()  # Will raise an error for non-200 responses

        data = response.json()
        if srcOrDest in ['src', 'source']:
            return self.create_source_config_from_tonic(data.get('sourceDatabase'), returnClass=True)
        elif srcOrDest in ['dest', 'destination']:
            return self.create_destination_config_from_tonic(data.get('destinationDatabase'), returnClass=True)
        else:
            raise ValueError("srcOrDest must be 'src'/'source' or 'dest'/'destination'")

    def update_source(self, workspace_id, workspace_config):
        update_url = self._get_url("/api/DataSource/source_db")
        workspace_config["workspaceId"] = workspace_id
        self._session.put(update_url, json=workspace_config).raise_for_status()

    def update_destination(self, workspace_id, workspace_config):
        update_url = self._get_url("/api/DataSource/destination_db")
        workspace_config["workspaceId"] = workspace_id
        self._session.put(update_url, json=workspace_config).raise_for_status()

    def generate_data(self, workspace_id):
        generate_url = self._get_url("/api/GenerateData/start")
        params = {"workspaceId": workspace_id, "diagnosticLogging": 'false'}
        response = self._session.post(generate_url, params=params)
        response.raise_for_status()  # Handle non-200 responses
        return response.json().get('id')

    def create_source_config_from_tonic(self, configuration, returnClass=False):
        conf = TonicConfiguration("source")
        conf.set_values(self.values_to_set)  # Initialize with default values
        conf.set_values(configuration)  # Update with actual configuration
        return conf if returnClass else conf.get_configuration()

    def create_destination_config_from_tonic(self, configuration, returnClass=False):
        conf = TonicConfiguration("destination")
        conf.set_values(self.values_to_set)  # Initialize with default values
        conf.set_values(configuration)  # Update with actual configuration
        return conf if returnClass else conf.get_configuration()

    def get_status(self, job_id, workspace_id, retryNum=0):
        status_url = f"{self._base_url}/api/job/{job_id}"
        response = self._session.get(status_url, headers={"accept": 'text/plain'})
        response.raise_for_status()
        data = response.json()
        status, message = data.get("status").split(' ')[0], data.get("errorMessages")
        progress, total_tasks, completed = self.process_task_list(data.get("tasks"))
        report = f"\nJob ID: {job_id}, Workspace ID: {workspace_id} has a current status of {status}.\n" \
                 f"Progress: {progress}% with {completed} of {total_tasks} tasks completed.\n" \
                 f"Retry has been attempted {retryNum} times.\n"
        return status, message, report, progress

    def process_task_list(self, task_list):
        total_tasks = len(task_list)
        tasks_completed, total_steps, steps_completed = 0, 0, 0
        for task in task_list:
            steps = task.get("totalSteps", 0)
            total_steps += steps
            if task.get("endTime"):
                steps_completed += steps
                tasks_completed += 1
            else:
                steps_completed += task.get("stepsCompleted", 0)
        percentage = round((steps_completed / total_steps) * 100) if total_steps else 0
        return percentage, total_tasks, tasks_completed

    def cancel_generation(self, job_id):
        cancel_url = self._get_url(f"/api/Job/{job_id}/cancel")
        self._session.post(cancel_url).raise_for_status()
        logging.info("Job Cancelled")

def main():
    tonic_url = os.getenv('TONIC_URL')
    tonic_api_key = os.getenv('TONIC_API_KEY')
    tonic_workspace_id = os.getenv('TONIC_WORKSPACE_ID')
    session = TonicSession(tonic_url, tonic_api_key)
    # Add your source and destination configuration JSON here
    source_config = {}
    destination_config = {}
    session.update_source(tonic_workspace_id, source_config)
    session.update_destination(tonic_workspace_id, destination_config)
    job_id = session.generate_data(tonic_workspace_id)
    session.get_status(job_id, tonic_workspace_id)

if __name__ == "__main__":
    main()
