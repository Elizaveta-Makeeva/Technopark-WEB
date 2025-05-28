import multiprocessing
import os

bind = "0.0.0.0:8000"
workers = 2
wsgi_app = "ask_makeeva.wsgi:application"


worker_class = "sync"
timeout = 30
keepalive = 2

limit_request_line = 4094

accesslog = "-"
errorlog = "-"
loglevel = "info"


max_requests = 1000
max_requests_jitter = 50