"""add auth security fields and tokens

Revision ID: 6136ce429d58
Revises: d11de3ce80cb
Create Date: 2026-07-30 11:04:11.343627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6136ce429d58'
down_revision: Union[str, None] = 'd11de3ce80cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- New auth token tables ---
    op.create_table(
        'email_verification_tokens',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('token_hash', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_email_verification_tokens_token_hash'),
        'email_verification_tokens', ['token_hash'], unique=True,
    )
    op.create_index(
        op.f('ix_email_verification_tokens_user_id'),
        'email_verification_tokens', ['user_id'], unique=False,
    )

    op.create_table(
        'password_reset_tokens',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('token_hash', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_password_reset_tokens_token_hash'),
        'password_reset_tokens', ['token_hash'], unique=True,
    )
    op.create_index(
        op.f('ix_password_reset_tokens_user_id'),
        'password_reset_tokens', ['user_id'], unique=False,
    )

    op.create_table(
        'refresh_tokens',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('token_hash', sa.String(length=128), nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('replaced_by_id', sa.Uuid(), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['replaced_by_id'], ['refresh_tokens.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=True,
    )
    op.create_index(
        op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False,
    )

    # --- New users columns ---
    # NOT NULL columns get a server_default so this migration is safe to run
    # against a `users` table that already has rows (existing accounts get
    # sensible defaults: not verified, zero failed attempts).
    op.add_column(
        'users',
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column('users', sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        'users',
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
    )
    op.add_column('users', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))

    # Drop the server_default once existing rows are backfilled — new inserts
    # should rely on the ORM-level Python default, not a permanent DB default.
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('email_verified', server_default=None)
        batch_op.alter_column('failed_login_attempts', server_default=None)

    # --- Extend the `userrole` enum: STUDENT, STAFF, ADMIN, SUPER_ADMIN
    # already exist (as their uppercase .name, which is how SQLAlchemy's
    # default Enum type persists PEP-435 enums); PARENT and NUTRITIONIST are
    # new. Postgres native enums require ALTER TYPE ... ADD VALUE, which
    # cannot run inside a transaction — hence the autocommit block. SQLite
    # has no native enum (Enum renders as VARCHAR + CHECK), so the CHECK
    # constraint is simply widened via a batch table rebuild.
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        with op.get_context().autocommit_block():
            op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'PARENT'")
            op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'NUTRITIONIST'")
    else:
        with op.batch_alter_table('users') as batch_op:
            batch_op.alter_column(
                'role',
                existing_type=sa.VARCHAR(length=11),
                type_=sa.Enum(
                    'STUDENT', 'PARENT', 'STAFF', 'NUTRITIONIST', 'ADMIN', 'SUPER_ADMIN',
                    name='userrole',
                ),
                existing_nullable=False,
            )


def downgrade() -> None:
    # Note: Postgres does not support removing values from a native ENUM
    # type without recreating it entirely; this downgrade leaves PARENT and
    # NUTRITIONIST as valid (but application-unused) values on Postgres. On
    # SQLite, the CHECK constraint is fully restored to the original 4.
    bind = op.get_bind()
    if bind.dialect.name != 'postgresql':
        with op.batch_alter_table('users') as batch_op:
            batch_op.alter_column(
                'role',
                existing_type=sa.Enum(
                    'STUDENT', 'PARENT', 'STAFF', 'NUTRITIONIST', 'ADMIN', 'SUPER_ADMIN',
                    name='userrole',
                ),
                type_=sa.VARCHAR(length=11),
                existing_nullable=False,
            )

    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'email_verified_at')
    op.drop_column('users', 'email_verified')

    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_token_hash'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')

    op.drop_index(op.f('ix_password_reset_tokens_user_id'), table_name='password_reset_tokens')
    op.drop_index(op.f('ix_password_reset_tokens_token_hash'), table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')

    op.drop_index(op.f('ix_email_verification_tokens_user_id'), table_name='email_verification_tokens')
    op.drop_index(op.f('ix_email_verification_tokens_token_hash'), table_name='email_verification_tokens')
    op.drop_table('email_verification_tokens')
