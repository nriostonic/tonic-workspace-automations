# tonic-workspace-automations

This README provides an overview and usage instructions for the code in this repository - which includes two main classes: TonicSession and TonicConfiguration. These classes are designed to facilitate interactions with the Tonic APIs for datasource updates, configuration management, data generation initiation, and job status monitoring.



## Requirements
- Python 3.6 or later
- requests library
- Access to a Tonic server with valid credentials

## Installation
Ensure Python and pip are installed on your system. Install the requests library using pip:

`pip install requests`

## TonicSession Class
### Overview
The TonicSession class manages sessions with the Tonic API, providing methods to configure data sources, initiate data generation, and retrieve job statuses.

### Initialization
To initialize a TonicSession object, provide the base URL of your Tonic server and your API key:

```
from tonic_client import TonicSession

base_url = 'https://your-tonic-server.com'
api_key = 'your_api_key'
session = TonicSession(base_url, api_key)
```

### Methods
- **get_configuration(workspace_id, srcOrDest)**: Retrieves the configuration for a specified workspace and database type (source or destination).
- **update_source(workspace_id, workspace_config)**: Updates the source database configuration for a given workspace.
- **update_destination(workspace_id, workspace_config)**: Updates the destination database configuration for a given workspace.
- **generate_data(workspace_id)**: Initiates data generation for the specified workspace.
- **get_status(job_id, workspace_id, retryNum)**: Retrieves the status of a data generation job.


## TonicConfiguration Class
### Overview
The TonicConfiguration class manages database configuration settings, supporting both default values and user modifications.

### Initialization
Create a new TonicConfiguration instance by specifying the database type (source or destination):

```
from tonic_client import TonicConfiguration

source_config = TonicConfiguration('source')
destination_config = TonicConfiguration('dest')
```

### Methods
- **set_value(key, value)**: Sets a specific configuration value.
- **set_values(values)**: Sets multiple configuration values at once.
- **get_value(key)**: Retrieves the value for a specific configuration key.
- **get_configuration()**: Returns the entire configuration as a dictionary.


## Example Usage
Below is an example script demonstrating how to use both classes. Please note that each class uses a set of default values that represent typical workspace configuration parameters. These include server address, port, authentication details, and more. You must update these defaults to reflect the actual configuration of your databases and correspond with the AddDataSourceResponseModel in our [swagger docs](https://app.tonic.ai/apidocs/index.html). 
```
from tonic_client import TonicSession, TonicConfiguration

# Initialize session
base_url = 'https://your-tonic-server.com'
api_key = 'your_api_key'
workspace_id = 'your_workspace_id'
session = TonicSession(base_url, api_key)

# Fetch and update source configuration
source_conf = session.get_configuration(workspace_id, 'src')
new_source_values = {'server': 'new_server', 'database': 'new_database'}
source_conf.set_values(new_source_values)
session.update_source(workspace_id, source_conf.get_configuration())

# Initiate data generation and check status
job_id = session.generate_data(workspace_id)
status, message, report, progress = session.get_status(job_id, workspace_id)
print(report)

```

## Logging 
The library uses Python's built-in logging module. You can configure logging level and format as needed in your application to get more detailed information about the API interactions.
