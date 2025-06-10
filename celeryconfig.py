# Celery Configuration for Certificate Generation
# Author: devag7 (Dev Agarwalla)

# Basic Celery configuration
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'

# Task settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True

# Task execution settings
task_always_eager = False
task_eager_propagates = True
task_ignore_result = False
task_store_eager_result = True