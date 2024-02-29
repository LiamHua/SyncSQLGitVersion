CREATE TRIGGER [trgMonitorStoredProcedureChanges]
ON DATABASE
FOR ALTER_PROCEDURE
AS
BEGIN
    DECLARE @StoredProcedureName NVARCHAR(255)
    DECLARE @Version INT;
    DECLARE @CreateUser VARCHAR(50) = SUSER_SNAME();
    DECLARE @ModifiedCode NVARCHAR(MAX)
   
    SET @StoredProcedureName = EVENTDATA().value('(/EVENT_INSTANCE/ObjectName)[1]', 'NVARCHAR(255)')
    SET @ModifiedCode = EVENTDATA().value('(/EVENT_INSTANCE/TSQLCommand/CommandText)[1]', 'NVARCHAR(MAX)')
    
    SELECT @Version = ISNULL(MAX(Version), 0)  FROM SQLGitVersion WHERE ProcedureName = @StoredProcedureName;
    SET @Version = @Version + 1;

    INSERT INTO SQLGitVersion(ProcedureName, Content, Version, CreateUser) VALUES (@StoredProcedureName, @ModifiedCode, @Version, @CreateUser)
END

ENABLE TRIGGER [trgMonitorStoredProcedureChanges] ON DATABASE