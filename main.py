# Description: This file is the main file for the project. It will be used to run the project.

import datetime
import sys
from Sync.syncSqVersion import SyncSqlVersion
from apscheduler.schedulers.blocking import BlockingScheduler


if __name__ == "__main__":
    sync_operate_jb = SyncSqlVersion("JB")
    sync_operate_tv = SyncSqlVersion("TV")
    sync_operate_sm = SyncSqlVersion("SM")
    sync_operate_zm = SyncSqlVersion("ZM")
    sync_operate_tx = SyncSqlVersion("TX")
    sync_operate_gy = SyncSqlVersion("GY")
    sync_operate_gywms = SyncSqlVersion("GYWMS")

    # 判断是否初始化仓库
    args = sys.argv
    if len(args) > 1 and args[1] == "init":
        sync_operate_jb.init_code_repository()
        sync_operate_tv.init_code_repository()
        sync_operate_sm.init_code_repository()
        sync_operate_zm.init_code_repository()
        sync_operate_tx.init_code_repository()
        sync_operate_gy.init_code_repository()
        sync_operate_gywms.init_code_repository()
    else:
        sync_operate_jb.clone_remote_repo()
        sync_operate_tv.clone_remote_repo()
        sync_operate_sm.clone_remote_repo()
        sync_operate_zm.clone_remote_repo()
        sync_operate_tx.clone_remote_repo()
        sync_operate_gy.clone_remote_repo()
        sync_operate_gywms.clone_remote_repo()

    # 定时任务，每3分钟执行一次
    scheduler = BlockingScheduler()
    interval = 180  # 间隔时间（秒）

    # 定义任务列表
    tasks = [
        sync_operate_jb.generate_update_and_push,
        sync_operate_tv.generate_update_and_push,
        sync_operate_sm.generate_update_and_push,
        sync_operate_zm.generate_update_and_push,
        sync_operate_tx.generate_update_and_push,
        sync_operate_gy.generate_update_and_push,
        sync_operate_gywms.generate_update_and_push,
    ]

    # 批量添加任务
    for task in tasks:
        scheduler.add_job(task, "interval", seconds=interval, next_run_time=datetime.now())

    # 启动定时任务
    scheduler.start()
