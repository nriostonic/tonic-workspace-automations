import logging
import copy

class TonicConfiguration:
    def __init__(self, db_type):
        """Initializes the TonicConfiguration object with default settings based on the database type."""
        logging.debug('Creating TonicConfiguration object')
        self._configuration = self._default_configuration(db_type)
        self._default_configuration = copy.deepcopy(self._configuration)

    def _default_configuration(self, db_type='default'):
        """Returns a default configuration dictionary based on the specified database type."""
        logging.debug('Creating default configuration')
        # Initialize default key-value pairs for configuration
        default_values = {
            "id": "", "server": "", "username": "", "password": "", "port": 0,
            "database": "", "databaseType": "", "sslEnabled": False, "trustServerCertificate": False,
            # Add other default configuration keys and values here
        }

        if db_type in ['source', 'src']:
            return {"sourceDatabase": default_values}
        elif db_type in ['destination', 'dest']:
            return {"destinationDatabase": default_values}
        else:
            return {"defaultDatabase": default_values}

    def set_value(self, key, value):
        """Sets a specific configuration value by key."""
        logging.debug(f'Setting {key} to {value}')
        if self._is_valid_value(key, value):
            self._set_nested_value(self._configuration, key, value)
        else:
            raise ValueError('Invalid configuration for key: {}'.format(key))

    def set_values(self, values):
        """Sets multiple configuration values from a dictionary."""
        logging.debug('Setting multiple values')
        if not isinstance(values, dict):
            raise ValueError("The values must be a dictionary")
        for key, value in values.items():
            self.set_value(key, value)

    def get_value(self, key):
        """Retrieves a specific configuration value by key."""
        logging.debug(f'Getting value for {key}')
        return self._get_nested_value(self._configuration, key)

    def _set_nested_value(self, config, key, value):
        """Recursively sets a value in a nested configuration dictionary."""
        keys = key.split('.')  # Support dot notation for nested dictionaries
        for part in keys[:-1]:
            config = config.setdefault(part, {})
        config[keys[-1]] = value

    def _get_nested_value(self, config, key):
        """Recursively retrieves a value from a nested configuration dictionary."""
        for part in key.split('.'):
            config = config.get(part)
            if config is None:
                return None
        return config

    def _is_valid_value(self, key, value):
        """Validates whether the specified value is appropriate for the given key."""
        # Implementation of validation logic based on key and value types
        # This is a placeholder for actual validation logic
        return True  # Assume all values are valid for simplicity

    def get_configuration(self):
        """Returns the entire configuration object."""
        return self._configuration
