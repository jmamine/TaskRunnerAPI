# app/routes.py

import logging

from flask import Blueprint, jsonify, request

from app import app
from app.docker_utils import (
    create_python_task,
    create_shell_task,
    delete_task,
    execute_task,
    list_tasks,
    start_powershell_task,
    start_python_task,
    stop_task,
    task_docker_info,
    task_schedule,
)
from app.utils import upload_script

task_blueprint = Blueprint('task', __name__)



# Get logger
logger = logging.getLogger(__name__)

# Error handler for 404 Not Found
@app.errorhandler(404)
def not_found_error(error):
    logger.error('Route not found: %s', request.path)
    return jsonify({'error': 'Not found'}), 404

# Error handler for 500 Internal Server Error
@app.errorhandler(500)
def internal_error(error):
    logger.error('Internal server error: %s', error)
    return jsonify({'error': 'Internal server error'}), 500


# python task route 
@task_blueprint.route('/py', methods=['POST'])
def handle_python_task():
    if request.form.get('upload') == 'true':
        task_id = upload_script(request)
        return start_python_task(task_id)
    else:
        return create_python_task(request)

# Shell task route 
@task_blueprint.route('/sh', methods=['POST'])
def handle_shell_task():
    if request.form.get('upload') == 'true':
        task_id = upload_script(request)
        return start_powershell_task(task_id)
    else:
        return create_shell_task(request)

# List tasks endpoint
@task_blueprint.route('/', methods=['GET'])
def list_tasks_route():
    try:
        return list_tasks()
    except Exception as e:
        logger.exception('An error occurred while listing tasks: %s', e)
        return jsonify({'error': 'An error occurred'}), 500
    
# manage tasks endpoint
@task_blueprint.route('/<task_id>', methods=['PUT', 'DELETE','GET'])
def manage_task_route(task_id):
    try:
        if request.method == 'PUT':
            return execute_task(task_id)
        elif request.method == 'GET':
            return task_docker_info(task_id)
        elif request.method == 'DELETE':
            return delete_task(task_id)
    except Exception as e:
        logger.exception('An error occurred while managing task: %s', e)
        return jsonify({'error': 'An error occurred'}), 500


# Stop task endpoint
@task_blueprint.route('/<task_id>/stop', methods=['POST'])
def stop_task_route(task_id):
    try:
        return stop_task(task_id)
    except Exception as e:
        logger.exception('An error occurred while stopping task: %s', e)
        return jsonify({'error': 'An error occurred'}), 500

# Schedule task endpoint
@task_blueprint.route('/<task_id>/schedule', methods=['POST'])
def task_schedule_route(task_id):
    try:
        cron_expression = request.form.get('cron_expression')
        return task_schedule(task_id, cron_expression)
    except Exception as e:
        logger.exception('An error occurred while scheduling task: %s', e)
        return jsonify({'error': 'An error occurred'}), 500