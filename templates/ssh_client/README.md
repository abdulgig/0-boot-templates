## template: github.com/zero-os/0-boot-templates/ssh_client/0.0.1

### Description:

This template is responsible for configuring the ssh client on Jumpscale. Initializing a service from this templates creates a client with the provided configuration.

If the client with instance name already already exists, that instance will be used

### Schema:

- `host`: Target host address
- `port`: Target port
- `login`: SSH username/login
- `password`: SSH password

### Actions:

- `delete`: Deletes the client from Jumpscale and the service
