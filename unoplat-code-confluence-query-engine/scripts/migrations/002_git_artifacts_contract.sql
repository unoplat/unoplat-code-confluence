-- RETIRED. This file is not an execution path and contains no destructive statements.
-- The contract is Alembic revision 0003_git_artifacts_contract, which also scrubs
-- historical event and error text and records its version in one transaction.
-- Follow ../../alembic/README.md. Running this file only raises the error below.
DO $$
BEGIN
  RAISE EXCEPTION '002_git_artifacts_contract.sql is retired; use Alembic revision 0003_git_artifacts_contract as described in alembic/README.md';
END;
$$;
