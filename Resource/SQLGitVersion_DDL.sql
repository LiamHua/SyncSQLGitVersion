-- dbo.SQLGitVersion definition

-- Drop table

-- DROP TABLE dbo.SQLGitVersion;

CREATE TABLE dbo.SQLGitVersion (
	Seq int IDENTITY(1,1) NOT NULL,
	ProcedureName varchar(100) COLLATE Chinese_PRC_CI_AS NULL,
	Content nvarchar(MAX) COLLATE Chinese_PRC_CI_AS NULL,
	Version int NULL,
	CreateDate datetime DEFAULT getdate() NULL,
	CreateUser varchar(100) COLLATE Chinese_PRC_CI_AS NULL,
	Upload int DEFAULT 0 NULL,
	CONSTRAINT SQLGitVersion_PK PRIMARY KEY (Seq)
);
 CREATE NONCLUSTERED INDEX IX_SQLGitVersion_ProcedureName ON dbo.SQLGitVersion (  ProcedureName ASC  )  
	 WITH (  PAD_INDEX = OFF ,FILLFACTOR = 100  ,SORT_IN_TEMPDB = OFF , IGNORE_DUP_KEY = OFF , STATISTICS_NORECOMPUTE = OFF , ONLINE = OFF , ALLOW_ROW_LOCKS = ON , ALLOW_PAGE_LOCKS = ON  )
	 ON [PRIMARY ] ;
 CREATE NONCLUSTERED INDEX IX_SQLGitVersion_Upload ON dbo.SQLGitVersion (  Upload ASC  )  
	 WITH (  PAD_INDEX = OFF ,FILLFACTOR = 100  ,SORT_IN_TEMPDB = OFF , IGNORE_DUP_KEY = OFF , STATISTICS_NORECOMPUTE = OFF , ONLINE = OFF , ALLOW_ROW_LOCKS = ON , ALLOW_PAGE_LOCKS = ON  )
	 ON [PRIMARY ] ;

-- Extended properties

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'存储过程名称', @level0type=N'Schema', @level0name=N'dbo', @level1type=N'Table', @level1name=N'SQLGitVersion', @level2type=N'Column', @level2name=N'ProcedureName';
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'内容', @level0type=N'Schema', @level0name=N'dbo', @level1type=N'Table', @level1name=N'SQLGitVersion', @level2type=N'Column', @level2name=N'Content';
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'版本号', @level0type=N'Schema', @level0name=N'dbo', @level1type=N'Table', @level1name=N'SQLGitVersion', @level2type=N'Column', @level2name=N'Version';
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'是否上传', @level0type=N'Schema', @level0name=N'dbo', @level1type=N'Table', @level1name=N'SQLGitVersion', @level2type=N'Column', @level2name=N'Upload';