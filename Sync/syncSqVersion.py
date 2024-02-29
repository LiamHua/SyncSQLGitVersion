# Description: Sync SQL file from JB to local
import codecs
import configparser
import datetime
import os
import re
import shutil
import stat
import time
import git
from Entity.SQLGitVersion import SQLGitVersion
from Util.sqlServerTool import SQLServerTool


class SyncSqlVersion:
    server_name = ""  # 服务器名称
    db_name = ""  # 数据库名称
    user = ""  # 用户名
    password = ""  # 密码
    git_url = ""  # Git仓库地址
    git_name = ""  # Git仓库名称
    git_branch = ""  # Git分支名称
    storage_path = ""  # 存储路径
    log_path = ""  # 日志路径
    is_init = False  # 是否初始化

    datasource_name = ""  # 数据源名称
    sql_tool = None

    def __init__(self, datasource_name):
        self.datasource_name = datasource_name
        self.init_config()

    # 初始化配置
    def init_config(self):
        # 读取配置文件
        self.read_config_file()

        # 创建 SQLServerTool 实例
        self.sql_tool = SQLServerTool(
            self.server_name, self.db_name, self.user, self.password
        )

    # 初始化代码仓库
    def init_code_repository(self):
        # 初始化Git仓库
        if self.is_init == "True":
            self.init_git_repo()

    # 创建Git仓库
    def init_git_repo(self):
        try:
            start_time = time.time()
            self.print_log(f"【SQL仓库初始化】开始")

            # 一、删除目录中的所有文件
            self.remove_all_files(self.storage_path)
            if not os.path.exists(self.storage_path):
                os.makedirs(self.storage_path)

            # 二、创建Git仓库
            repo = git.Repo.init(self.storage_path)

            # 三、从数据库中获取数据,先全部置为未提交状态
            self.init_commit_status()
            sqlGitVersion_array = self.get_init_data()
            self.print_log(f"【SQL仓库初始化】待初始化文件数量：{len(sqlGitVersion_array)}")

            # 四、创建文件
            self.create_files(sqlGitVersion_array)

            # 五、提交到本地仓库
            repo.git.add(A=True)
            repo.git.commit(m=f"{self.datasource_name} SQL仓库初始化")

            # 六、创建远程仓库并推送，然后更新提交状态
            repo.create_remote(self.git_name, self.git_url)
            repo.git.push("--set-upstream", self.git_name, self.git_branch)
            self.batch_update_commit_status(sqlGitVersion_array)
            self.print_log(f"【SQL仓库初始化】推送成功")

            end_time = time.time()
            self.print_log(f"【SQL仓库初始化】总共耗时：{int(end_time - start_time)}秒")
        except Exception as e:
            self.print_log("【SQL仓库初始化】失败")
            self.print_log(e)

    # 生成更新并推送
    def generate_update_and_push(self):
        try:
            start_time = time.time()
            self.print_log(f"【SQL仓库更新】开始")

            # 一、拉取远程仓库
            repo = git.Repo(self.storage_path)
            repo.git.pull()

            # 二、从数据库中获取未提交数据
            sqlGitVersion_array = self.get_uncommitted_data()
            self.print_log(f"【SQL仓库更新】待更新文件数量：{len(sqlGitVersion_array)}")

            # 三、创建文件并提交到本地仓库
            if len(sqlGitVersion_array) == 0:
                self.print_log(f"【SQL仓库更新】无需更新")
                return

            for obj in sqlGitVersion_array:
                file_name = self.create_file(obj)
                repo.git.add(file_name)

                create_date = obj.create_date.strftime("%Y-%m-%d %H:%M:%S")

                if obj.version == 1:
                    msg = f"存储过程新增-[{obj.procedure_name}]-[{obj.create_user}]-[{create_date}]"
                else:
                    msg = f"存储过程更新-[{obj.procedure_name}]-[{obj.create_user}]-[{create_date}]"

                if repo.index.diff("HEAD"):
                    repo.git.commit(m=msg)

            # 四、推送到远程仓库，然后更新提交状态
            repo.git.push(self.git_name, self.git_branch)
            self.batch_update_commit_status(sqlGitVersion_array)
            self.print_log(f"【SQL仓库更新】推送成功")

            end_time = time.time()
            self.print_log(f"【SQL仓库更新】总共耗时：{int(end_time - start_time)}秒")
        except Exception as e:
            self.print_log("【SQL仓库更新】失败")
            self.print_log(e)

    # 克隆远程仓库
    def clone_remote_repo(self):
        if self.is_init == True:
            return
        try:
            start_time = time.time()
            self.print_log(f"【SQL仓库克隆】开始")

            # 一、删除目录中的所有文件
            self.remove_all_files(self.storage_path)
            if not os.path.exists(self.storage_path):
                os.makedirs(self.storage_path)

            # 二、克隆远程仓库
            git.Repo.clone_from(self.git_url, self.storage_path, branch=self.git_branch)

            end_time = time.time()
            self.print_log(f"【SQL仓库克隆】总共耗时：{int(end_time - start_time)}秒")
        except Exception as e:
            self.print_log("【SQL仓库克隆】失败")
            self.print_log(e)

    # 获取数据库中初始化数据
    def get_init_data(self):
        self.sql_tool.connect()
        sqlGitVersion_array = []
        # 执行查询
        self.sql_tool.execute_query(
            "SELECT * FROM SQLGitVersion Where Version = 1 Order By Seq Asc"
        )

        # 获取结果
        rows = self.sql_tool.fetch_all()
        for row in rows:
            # 创建 SQLGitVersion 实例
            sqlGitVersion = SQLGitVersion(
                row.Seq,
                row.ProcedureName,
                row.Content,
                row.Version,
                row.CreateDate,
                row.CreateUser,
            )
            sqlGitVersion_array.append(sqlGitVersion)

        # 关闭连接
        self.sql_tool.close()
        return sqlGitVersion_array

    # 获取未提交的数据
    def get_uncommitted_data(self):
        self.sql_tool.connect()

        sqlGitVersion_array = []
        # 执行查询
        self.sql_tool.execute_query(
            "SELECT * FROM SQLGitVersion Where Upload = 0 Order By Seq Asc"
        )

        # 获取结果
        rows = self.sql_tool.fetch_all()
        for row in rows:
            # 创建 SQLGitVersion 实例
            sqlGitVersion = SQLGitVersion(
                row.Seq,
                row.ProcedureName,
                row.Content,
                row.Version,
                row.CreateDate,
                row.CreateUser,
            )
            sqlGitVersion_array.append(sqlGitVersion)

        # 关闭连接
        self.sql_tool.close()
        return sqlGitVersion_array

    # 批量提交已更新状态
    def batch_update_commit_status(self, sqlGitVersion_array):
        self.sql_tool.connect()

        for obj in sqlGitVersion_array:
            self.sql_tool.execute_query(
                f"UPDATE SQLGitVersion SET Upload = 1 WHERE Seq = {obj.seq}"
            )
            self.sql_tool.conn.commit()
        self.sql_tool.close()

    # 单个提交已更新状态
    def update_commit_status(self, sqlGitVersion):
        self.sql_tool.connect()
        self.sql_tool.execute_query(
            f"UPDATE SQLGitVersion SET Upload = 1 WHERE Seq = {sqlGitVersion.seq}"
        )
        self.sql_tool.conn.commit()
        self.sql_tool.close()

    # 全部置为未提交状态
    def init_commit_status(self):
        self.sql_tool.connect()
      
        self.sql_tool.execute_query(
            f"UPDATE SQLGitVersion SET Upload = 0"
        )
        self.sql_tool.conn.commit()
        self.sql_tool.close()

    # 批量创建文件
    def create_files(self, sqlGitVersion_array):
        for obj in sqlGitVersion_array:
            content = obj.content if obj.content is not None else ""
            file_name = re.sub(r'[\\/:*?"<>|\r\n|\t]+', "", obj.procedure_name) + ".sql"

            if not os.path.exists(self.storage_path):
                os.makedirs(self.storage_path)
            # 将 content 写入到文件中
            try:
                file_path = os.path.join(self.storage_path, file_name)
                with codecs.open(file_path, "w", "utf-8") as file:
                    file.write(content)
            except Exception as e:
                self.print_log("写入文件失败:" + file_name)
                self.print_log(file_path)
                self.print_log(e)
                return

    # 单个创建文件
    def create_file(self, sqlGitVersion):
        content = sqlGitVersion.content if sqlGitVersion.content is not None else ""
        file_name = (
            re.sub(r'[\\/:*?"<>|\r\n|\t]+', "", sqlGitVersion.procedure_name) + ".sql"
        )

        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        # 将 content 写入到文件中
        try:
            file_path = os.path.join(self.storage_path, file_name)
            with codecs.open(file_path, "w", "utf-8") as file:
                file.write(content)
        except Exception as e:
            self.print_log("写入文件失败:" + file_name)
            self.print_log(file_path)
            self.print_log(e)
            return
        return file_name

    # 读取配置文件
    def read_config_file(self):
        config = configparser.ConfigParser()
        config.read("db.ini", encoding="utf-8")

        datasource_info = config[self.datasource_name]
        self.server_name = datasource_info["server_name"]
        self.db_name = datasource_info["db_name"]
        self.user = datasource_info["user"]
        self.password = datasource_info["password"]
        self.git_url = datasource_info["git_url"]
        self.git_name = datasource_info["git_name"]
        self.git_branch = datasource_info["git_branch"]
        self.storage_path = datasource_info["storage_path"]
        self.log_path = datasource_info["log_path"]
        self.is_init = datasource_info["is_init"]

    # 删除目录中的所有文件和文件夹
    def remove_all_files(self, storage_path):
        if os.path.exists(storage_path):
            shutil.rmtree(storage_path, onerror=self.delete)

    # 删除文件或文件夹
    def delete(self, func, path, execinfo):
        os.chmod(path, stat.S_IWUSR)
        func(path)

    # 打印日志
    def print_log(self, msg):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{current_time}] - 【{self.datasource_name}】{msg}"
        print(log_message)

        # 写入日志文件
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)

        # 消息中包含失败字样，写入到 error.log 文件中
        if "失败" in log_message or isinstance(msg, Exception):
            log_file_path = os.path.join(self.log_path, "error.log")
        else:
            log_file_path = os.path.join(self.log_path, "out.log")

        with codecs.open(log_file_path, "a", "utf-8") as file:
            file.write(log_message + "\n")

        with codecs.open("all.log", "a", "utf-8") as file:
            file.write(log_message + "\n")
