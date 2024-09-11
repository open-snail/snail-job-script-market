import time
import psutil

from log import SnailLog
from schemas import ExecuteResult
from snail import job
import json

import platform
from datetime import datetime

@job("serverMonitorJob")
def test_job_executor(args: str) -> ExecuteResult:
    SnailLog.REMOTE.info("Starting to log server information... " + args)
    log_system_info(args)
    return ExecuteResult.success()


def get_system_info():
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 获取平台信息
    system_info = platform.uname()

    # 获取 CPU 信息
    cpu_usage = psutil.cpu_percent(interval=1)

    # 获取内存信息
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total / (1024 ** 3)  # 转换为 GB
    used_memory = memory_info.used / (1024 ** 3)  # 转换为 GB
    memory_percent = memory_info.percent

    # 获取磁盘信息
    disk_info = psutil.disk_usage('/')
    total_disk = disk_info.total / (1024 ** 3)  # 转换为 GB
    used_disk = disk_info.used / (1024 ** 3)  # 转换为 GB
    disk_percent = disk_info.percent

    # 这可以写数据库等其他的持久化操作, 这里只是演示先上报日志
    info = (
        f"Time: {current_time}\n"
        f"System: {system_info.system} {system_info.release} ({system_info.version})\n"
        f"Machine: {system_info.machine}\n"
        f"CPU Usage: {cpu_usage}%\n"
        f"Total Memory: {total_memory:.2f} GB, Used Memory: {used_memory:.2f} GB ({memory_percent}%)\n"
        f"Total Disk: {total_disk:.2f} GB, Used Disk: {used_disk:.2f} GB ({disk_percent}%)\n"
        "----------------------------------------\n"
    )

    SnailLog.REMOTE.info(info)
    return info

def log_system_info(args: str):
    job_params = json.loads(json.loads(args).get("jobParams"))
    print(job_params)
    total = 1
    interval = 1
    # job执行一次, 本地可以多次采集信息, 可以提高准确度
    if job_params['total']:
        total = job_params['total']
    # 多久采集一次
    if job_params['interval']:
        interval = job_params['interval']

    while total > 0:
        # 获取系统信息
        system_info = get_system_info()

        # 打印到控制台
        print(system_info)

        # 写入日志文件
        with open("server_info_log.txt", "a") as log_file:
            log_file.write(system_info)

        # 每隔 N 秒执行一次
        time.sleep(interval)
        total = total - 1
