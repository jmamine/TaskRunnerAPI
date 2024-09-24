This project is a backend application designed to manage and execute tasks within Docker containers. It provides a RESTful API for interacting with the task execution system. The backend is built using Flask, a lightweight WSGI web application framework, and Docker containers for task isolation and execution.

## Features

- Create and execute Python script tasks.
- Create and execute Shell script tasks.
- List all tasks along with their statuses.
- Execute, stop, schedule, and delete tasks.
- Retrieve detailed information about tasks and associated Docker containers.

## Installation

1. Navigate to the project directory: `cd Hiring-software-engineer-backend`.
2. Copy the `.env.example` file to a new file named `.env`
3. Install the required dependencies: `pip install -r requirements.txt`.
4. open Docker Desktop.
5. Run the application: `python run.py`.
6. The application should now be running on http://localhost:5000.

# API Endpoints Documentation

## POST /task/py

Create a Python script task.

### Input

Form-data:

- `file`: Python script file.
- `requirements` (optional): Requirements file.
- `upload` (boolean): If true, the script will be uploaded and executed. Otherwise, it will be executed directly in a Docker container without being uploaded.

### Output

JSON response:

- `message`: Indicates task creation status.
- `script_type`: Indicates the script type (python).
- `task_id`: Unique identifier for the task.

### Functionality

- Accepts a Python script file and optionally a requirements file.
- If `upload` is true, the script is uploaded and executed.
- If `upload` is false, the script is executed directly in a Docker container as a flux.
- Creates a Docker container to execute the Python script.

## POST /task/sh

Create a Shell script task.

### Input

Form-data:

- `file`: Shell script file.
- `upload` (boolean): If true, the script will be uploaded and executed. Otherwise, it will be executed directly in a Docker container without being uploaded.

### Output

JSON response:

- `message`: Indicates task creation status.
- `script_type`: Indicates the script type (shell).
- `task_id`: Unique identifier for the task.

### Functionality

- Accepts a Shell script file.
- If `upload` is true, the script is uploaded and executed.
- If `upload` is false, the script is executed directly in a Docker container as a flux.
- Creates a Docker container to execute the Shell script.

## GET /task/

List all tasks.

### Input

None.

### Output

JSON response:

- List of tasks, each with `task_id`, `status`, and `script_type`.

### Functionality

- Lists all tasks along with their statuses and script types.

## PUT /task/<task_id>

Execute a specific task.

### Input

None.

### Output

JSON response with a message indicating successful task execution or an error message if an error occurs.

### Functionality

- Executes a specific task by its `task_id`.

## DELETE /task/<task_id>

Delete a specific task.

### Input

None.

### Output

JSON response with a message indicating successful task deletion or an error message if an error occurs.

### Functionality

- Deletes a specific task by its `task_id`.

## POST /task/<task_id>/stop

Stop a specific task.

### Input

None.

### Output

JSON response with a message indicating successful task stoppage or an error message if an error occurs.

### Functionality

- Stops a specific task by its `task_id`.

## POST /task/<task_id>/schedule

Schedule a specific task.

### Input

Form-data:

- `cron_expression`: CRON expression to schedule the task.

### Output

JSON response with a message indicating successful task scheduling or an error message if an error occurs.

### Functionality

- Schedules a specific task using a CRON expression.

## GET /<task_id>

Retrieve Docker information for a specific task.

### Input

None.

### Output

JSON response with Docker information for the specified task.

### Functionality

- Retrieves detailed Docker container information for a specific task by its `task_id`.

## Usage

- Use the provided endpoints to create, manage, and execute tasks.
- Use CRON expressions to schedule tasks for automatic execution.
