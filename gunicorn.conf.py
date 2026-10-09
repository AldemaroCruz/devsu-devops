import os

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = int(os.getenv("WEB_CONCURRENCY", "2"))
threads = 2
timeout = 30
graceful_timeout = 30
accesslog = "-"
errorlog = "-"
worker_tmp_dir = "/tmp"

# Management is handled by the container orchestrator.
control_socket_disable = True
