# Database migrations

`001_initial_schema.sql` is mounted into the local PostgreSQL container and runs automatically on first initialization. Later changes should use numbered migrations and be applied by Alembic once the service database layer is introduced.

