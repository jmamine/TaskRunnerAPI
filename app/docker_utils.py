# app/docker_utils.py

import base64
import io
import logging
import os
import uuid

from apscheduler.triggers.cron import CronTrigger
from flask import jsonify

from app import app, client, scheduler

# from app import logger 

# Get logger
logger = logging.getLogger(__name__)



# Containerized Task Execution

tasks = {}

def create_python_task(request):
    try:
        code_file = request.files.get('file')  
        requirements_file = request.files.get('requirements')  

        # Read the content of the uploaded Python file
        code = code_file.read().decode('utf-8')

        # Read the content of the requirements file
        requirements = requirements_file.read().decode('utf-8') if requirements_file else ''

        # Encode the user's code and requirements using base64
        encoded_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')
        encoded_requirements = base64.b64encode(requirements.encode('utf-8')).decode('utf-8')

        # Define Dockerfile content to create a Python script container
        dockerfile_content = f'''
        FROM python:3.8

        WORKDIR /app
        COPY . .
        RUN echo {encoded_requirements} | base64 -d > requirements.txt && pip install -r requirements.txt
        CMD python -c "$(echo '{encoded_code}' | base64 -d)"
        '''

        # Build Docker image from Dockerfile content
        image, _ = client.images.build(
            fileobj=io.BytesIO(dockerfile_content.encode('utf-8')),
            rm=True)

        # Run a container from the built image
        container = client.containers.run(image, detach=True)

        # Generate a unique task ID
        task_id = str(uuid.uuid4())

        # Store the task, its corresponding container, and script type in the tasks dictionary
        tasks[task_id] = {'container': container, 'script_type': 'python'}

        return jsonify({"message": f"Task {task_id} created successfully!", "script_type": "python", "task_id": task_id})
    except Exception as e:
        logger.exception('An error occurred while creating Python task: %s', e)
        return jsonify({'error': 'An error occurred'}), 500

def create_shell_task(request):
    try:
        code_file = request.files.get('file') 

        # Read the content of the uploaded Python file
        code = code_file.read().decode('utf-8')

        # Encode the user's code using base64
        encoded_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')

        # Define Dockerfile content to create a Python script container
        dockerfile_content = f'''
        FROM mcr.microsoft.com/powershell

        WORKDIR /app
        COPY . .
        CMD pwsh -c "$(echo '{encoded_code}' | base64 -d)"
        '''

        # Build Docker image from Dockerfile content
        image, _ = client.images.build(fileobj=io.BytesIO(dockerfile_content.encode('utf-8')), rm=True)

        # Run a container from the built image
        container = client.containers.run(image, detach=True)

        # Generate a unique task ID
        task_id = str(uuid.uuid4())

        # Store the task, its corresponding container, and script type in the tasks dictionary
        tasks[task_id] = {'container': container, 'script_type': 'shell'}

        return jsonify({"message": f"Task {task_id} created successfully!", "script_type": "shell", "task_id": task_id})
    except Exception as e:
        logger.exception('An error occurred while creating Shell task: %s', e)
        return jsonify({'error': 'An error occurred'}), 500

def execute_task(task_id):
    try:
        
        if task_id not in tasks:
            return f"Task {task_id} not found", 404

        # Get the container associated with the task
        container = tasks[task_id]['container']

        # Start the container (if not already running)
        if container.status != 'running':
            start_container(task_id)

        return "Task executed successfully in Docker container!"
    except Exception as e:
        logger.exception('An error occurred while executing task: %s', e)
        return jsonify({'error': 'An error occurred'}), 500

def list_tasks():
    try:
        task_list = [{'task_id': task_id, 'status': container.status, 'script_type': tasks[task_id]['script_type']}
                     for task_id, task_info in tasks.items()
                     for container in [task_info['container']]]
        return jsonify(task_list)
    except Exception as e:
        logger.exception('An error occurred while listing tasks: %s', e)
        return jsonify({'error': 'An error occurred'}), 500

def delete_task(task_id):
    try:
        
        if task_id not in tasks:
            return f"Task {task_id} not found", 404

        # Get the container associated with the task
        container = tasks.pop(task_id)['container']

        # Stop and remove the container
        container.stop()
        container.remove()

        return f"Task {task_id} deleted successfully!"
    except Exception as e:
        logger.exception('An error occurred while deleting task: %s', e)
        return jsonify({'error': 'An error occurred'}), 500

def stop_task(task_id):
    try:
        
        if task_id not in tasks:
            return f"Task {task_id} not found", 404

        # Get the container associated with the task
        container = tasks[task_id]['container']

        # Stop the container
        container.stop()

        return f"Task {task_id} stopped successfully!"
    except Exception as e:
        logger.exception('An error occurred while stopping task: %s', e)
        return jsonify({'error': 'An error occurred'}), 500

def task_schedule(task_id, cron_expression):
    try:
        
        # Get the container associated with the task
        container = tasks[task_id]['container']

        # Define a function to start the container

        # Start the container (if not already running)
        if container.status != 'running':
             scheduler.add_job(start_container, CronTrigger.from_crontab(cron_expression), args=[task_id], id=task_id)

        return "Task executed successfully in Docker container!"
    except Exception as e:
        logger.exception('An error occurred while scheduling task: %s', e)
        return jsonify({'error': 'An error occurred'}), 500

def start_container(task_id):
    try:
        container = tasks[task_id]['container']
        container.start()
    except Exception as e:
        logger.exception('An error occurred while starting container for task %s: %s', task_id, e)




def start_powershell_task(task_id):
    try:
    
        # Create the task folder if it doesn't exist
        task_folder = os.path.join(app.config['UPLOAD_FOLDER'], task_id)
        os.makedirs(task_folder, exist_ok=True)
        os.rename(os.path.join(task_folder, 'code.py'), os.path.join(task_folder, 'script.ps1'))
        

        
        # Create Dockerfile content for PowerShell
        dockerfile_content = '''
            FROM mcr.microsoft.com/powershell

            # Set the working directory in the container
            WORKDIR /app

            # Copy the PowerShell script into the container
            COPY script.ps1 .

            # Command to run the PowerShell script
            CMD ["pwsh", "-File", "script.ps1"]
            '''

        # Write Dockerfile content to the task folder

        with open(os.path.join(task_folder, 'Dockerfile'), 'w') as dockerfile:
            dockerfile.write(dockerfile_content)

        # Build Docker image from the task folder
        image, _ = client.images.build(
            path=task_folder,
            dockerfile ='Dockerfile',
            rm=True,
            tag=f"task_{task_id}"
        )

        # Run a container from the built image
        container = client.containers.run(image, detach=True)

        # Store the task, its corresponding container, and script type in the tasks dictionary
        tasks[task_id] = {'container': container, 'script_type': 'shell'}

        return jsonify({"message": f"Task {task_id} created successfully!", "script_type": "shell", "task_id": task_id})
    except Exception:
        logger.exception("Error occurred during PowerShell task creation:")
        return jsonify({"error": "An error occurred during PowerShell task creation"}), 500
    



def start_python_task(task_id):
    try:
        
        # Create the task folder if it doesn't exist
        task_folder = os.path.join(app.config['UPLOAD_FOLDER'], task_id)
        os.makedirs(task_folder, exist_ok=True)
        
        # Create Dockerfile content
        dockerfile_content = '''
            FROM python:3.8

            # Set the working directory in the container
            WORKDIR /app

            # Copy the requirements file into the container
            COPY requirements.txt .

            # Install Python dependencies
            RUN pip install -r requirements.txt

            # Copy the Python script into the container
            COPY code.py .

            # Command to run the Python script
            CMD ["python", "code.py"]
            '''

        # Write Dockerfile content to the task folder
        with open(os.path.join(task_folder, 'Dockerfile'), 'w') as dockerfile:
            dockerfile.write(dockerfile_content)

        # Build Docker image from the task folder
        image, _ = client.images.build(
            path=task_folder,
            dockerfile='Dockerfile',
            rm=True,
            tag=f"task_{task_id}"
        )

        # Run a container from the built image
        container = client.containers.run(image, detach=True)

        # Store the task, its corresponding container, and script type in the tasks dictionary
        tasks[task_id] = {'container': container, 'script_type': 'python'}

        return jsonify({"message": f"Task {task_id} created successfully!", "script_type": "python", "task_id": task_id})
    except Exception:
        logger.exception("Error occurred during Python task creation:")
        return jsonify({"error": "An error occurred during Python task creation"}), 500    
    


def task_docker_info(task_id):
    try:
        if task_id not in tasks:
            return f"Task {task_id} not found", 404

        # Get the container associated with the task
        container = tasks[task_id]['container']

        # Get container information
        container_info = {
            'id': container.id,
            'name': container.name,
            'status': container.status,
            'created_at': container.attrs['Created'],
            'started_at': container.attrs['State']['StartedAt'] if container.attrs['State']['StartedAt'] else None,
            'finished_at': container.attrs['State']['FinishedAt'] if container.attrs['State']['FinishedAt'] else None
        }

        # # Get Docker image information
       
        image_id = container.attrs['Image']
        image_info = client.images.get(image_id)
        image_name = image_info.tags[0] if image_info.tags else None
        created_at = image_info.attrs['Created']
        size = image_info.attrs['Size']

        # Construct image information dictionary
        image_info = {
            'id': image_id,
            'name': image_name,
            'created_at': created_at,
            'size': size
        }

        # Assemble all Docker information
        docker_info = {
            'container': container_info,
            'image': image_info
        }

        return jsonify(docker_info)
    except Exception as e:
        logger.exception('An error occurred while retrieving Docker information for task %s: %s', task_id, e)
        return jsonify({'error': 'An error occurred'}), 500