1. Repository 

```
CREATE TABLE repository (
    repository_name        TEXT NOT NULL,
    repository_owner_name  TEXT NOT NULL,
    PRIMARY KEY (repository_name, repository_owner_name)
);
```

2. codebase_config (static metadata per codebase)

```
CREATE TABLE codebase_config (
    repository_name        TEXT NOT NULL,
    repository_owner_name  TEXT NOT NULL,
    root_package           TEXT NOT NULL,               -- primary key inside codebase_folder
    source_directory       TEXT NOT NULL,
    programming_language_metadata JSONB NOT NULL,

    PRIMARY KEY (repository_name, repository_owner_name, root_package),
    FOREIGN KEY (repository_name, repository_owner_name)
        REFERENCES repository (repository_name, repository_owner_name)
        ON DELETE CASCADE
);
```

3. repository_workflow_run 

```
CREATE TABLE repository_workflow_run (
    repository_name        TEXT NOT NULL,
    repository_owner_name  TEXT NOT NULL,
    repository_workflow_id TEXT NOT NULL,      -- constant across runs
    repository_workflow_run_id TEXT NOT NULL,  -- unique per run

    status         TEXT NOT NULL CHECK (status IN
                   ('SUBMITTED','RUNNING','FAILED','TIMED_OUT','COMPLETED')),
    error_report   JSONB,
    started_at     TIMESTAMPTZ NOT NULL,
    completed_at   TIMESTAMPTZ,

    PRIMARY KEY (
        repository_name,
        repository_owner_name,
        repository_workflow_run_id
    ),
    FOREIGN KEY (repository_name, repository_owner_name)
        REFERENCES repository (repository_name, repository_owner_name)
        ON DELETE CASCADE
);

-- fast “latest run for repo” query
CREATE INDEX idx_repo_latest_run
  ON repository_workflow_run (repository_name,
                              repository_owner_name,
                              started_at DESC);
```

4. codebase_workflow_run (child-workflow runs)

```
CREATE TABLE codebase_workflow_run (
    repository_name        TEXT NOT NULL,
    repository_owner_name  TEXT NOT NULL,
    root_package           TEXT NOT NULL,           -- FK to codebase_config
    codebase_workflow_id   TEXT NOT NULL,
    codebase_workflow_run_id TEXT NOT NULL,

    -- link back to parent repo run (optional but handy)
    repository_workflow_run_id TEXT NOT NULL,

    status         TEXT NOT NULL CHECK (status IN
                   ('SUBMITTED','RUNNING','FAILED','TIMED_OUT','COMPLETED')),
    error_report   JSONB,
    started_at     TIMESTAMPTZ NOT NULL,
    completed_at   TIMESTAMPTZ,

    PRIMARY KEY (
        repository_name,
        repository_owner_name,
        root_package,
        codebase_workflow_run_id
    ),

    FOREIGN KEY (repository_name, repository_owner_name, root_package)
        REFERENCES codebase_config (repository_name,
                                    repository_owner_name,
                                    root_package)
        ON DELETE CASCADE,

    FOREIGN KEY (repository_name, repository_owner_name,
                 repository_workflow_run_id)
        REFERENCES repository_workflow_run (repository_name,
                                            repository_owner_name,
                                            repository_workflow_run_id)
        ON DELETE CASCADE
);

-- find latest child-workflow run for a codebase quickly
CREATE INDEX idx_codebase_latest_run
  ON codebase_workflow_run (repository_name,
                            repository_owner_name,
                            root_package,
                            started_at DESC);
```