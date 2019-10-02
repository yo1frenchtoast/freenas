from logging.config import fileConfig
import os

from alembic import context
from alembic.operations import ops
from alembic.operations.base import BatchOperations, Operations
from alembic.operations.batch import ApplyBatchImpl, BatchOperationsImpl
from sqlalchemy import engine_from_config, ForeignKeyConstraint, pool

import middlewared
from middlewared.sqlalchemy import JSON, Model
from middlewared.utils import load_modules

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Model.metadata
list(load_modules(os.path.join(os.path.dirname(middlewared.__file__), "plugins")))
list(load_modules("/usr/local/lib/middlewared_truenas/plugins"))

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


@Operations.register_operation("drop_references")
@BatchOperations.register_operation("drop_references", "batch_drop_references")
class DropReferencesOp(ops.MigrateOperation):
    def __init__(
        self,
        field_name,
        table_name,
    ):
        self.field_name = field_name
        self.table_name = table_name

    @classmethod
    def drop_references(cls, operations):
        raise RuntimeError()

    @classmethod
    def batch_drop_references(cls, operations, field_name):
        op = cls(
            field_name,
            operations.impl.table_name,
        )
        return operations.invoke(op)


@Operations.implementation_for(DropReferencesOp)
def drop_references(operations, operation):
    operations.impl.drop_references(
        operation.field_name,
    )


def drop_references_impl(self, column_name):
    for constraint in self.unnamed_constraints:
        if isinstance(constraint, ForeignKeyConstraint) and len(constraint.columns) == 1:
            if list(constraint.columns)[0].name == column_name:
                self.unnamed_constraints.remove(constraint)
                break


BatchOperationsImpl.drop_references = lambda self, column: self.batch.append(("drop_references", (column,), {}))
ApplyBatchImpl.drop_references = drop_references_impl


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in {"sqlite_sequence"}:
        return False
    else:
        return True


def render_item(type_, obj, autogen_context):
    """Apply custom rendering for selected items."""

    if isinstance(obj, JSON):
        return "sa.TEXT()"

    # default rendering for other objects
    return False


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        render_as_batch=True,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            include_object=include_object,
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()