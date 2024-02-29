class SQLGitVersion:
    def __init__(self, seq, procedure_name, content, version, create_date, create_user):
        self.seq = seq  # int类型
        self.procedure_name = procedure_name  # string类型
        self.content = content  # string类型
        self.version = version  # int类型
        self.create_date = create_date  # 时间类型
        self.create_user = create_user  # string类型
