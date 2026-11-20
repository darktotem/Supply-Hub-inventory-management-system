
"""update invoice schema

Revision ID: 6b1dc058f36b
Revises: 6083db403890
Create Date: 2026-11-18 09:29:36.348937

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b1dc058f36b'
down_revision = '6083db403890'
branch_labels = None
depends_on = None


def upgrade():
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('method', sa.String(length=20), nullable=False),
        sa.Column('reference', sa.String(length=64), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("method IN ('cash','mpesa','bank','card')", name='ck_payment_method'),
        sa.CheckConstraint('amount > 0', name='ck_payment_amount_positive'),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference')
    )

    op.create_index(
        'ix_payments_invoice_id',
        'payments',
        ['invoice_id'],
        unique=False
    )

    # Update audit_logs table
    with op.batch_alter_table(
        'audit_logs',
        naming_convention={
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
        }
    ) as batch_op:
        batch_op.add_column(sa.Column('old_values', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('new_values', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('prev_hash', sa.String(length=64), nullable=False))
        batch_op.add_column(sa.Column('hash', sa.String(length=64), nullable=False))

        batch_op.alter_column(
            'entity',
            existing_type=sa.VARCHAR(length=50),
            type_=sa.String(length=30),
            existing_nullable=False
        )

        batch_op.alter_column(
            'entity_id',
            existing_type=sa.INTEGER(),
            nullable=False
        )

        batch_op.alter_column(
            'action',
            existing_type=sa.VARCHAR(length=50),
            type_=sa.String(length=20),
            existing_nullable=False
        )

        batch_op.alter_column(
            'user_id',
            existing_type=sa.INTEGER(),
            nullable=True
        )

        batch_op.alter_column(
            'created_at',
            existing_type=sa.DATETIME(),
            type_=sa.String(length=40),
            nullable=False
        )

        batch_op.create_index('ix_audit_logs_entity', ['entity'], unique=False)
        batch_op.create_index('ix_audit_logs_entity_id', ['entity_id'], unique=False)
        batch_op.create_unique_constraint('uq_audit_logs_hash', ['hash'])
        if op.get_bind().dialect.name == "postgresql":
            # Postgres auto-named the unnamed FK created in the initial migration
            batch_op.drop_constraint('audit_logs_user_id_fkey', type_='foreignkey')
        else:
            batch_op.drop_constraint('fk_audit_logs_user_id_users', type_='foreignkey')
            
        batch_op.drop_column('details')

    # Update invoices table
    with op.batch_alter_table(
        'invoices',
        naming_convention={
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
        }
    ) as batch_op:
        batch_op.add_column(
            sa.Column('total', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0')
        )
        batch_op.add_column(
            sa.Column('amount_paid', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0')
        )
        batch_op.add_column(
            sa.Column('status', sa.String(length=10), nullable=False, server_default='pending')
        )
        batch_op.add_column(sa.Column('sale_id', sa.Integer(), nullable=True))

        batch_op.create_foreign_key(
            'fk_invoices_sale_id_customer_history',
            'customer_history',
            ['sale_id'],
            ['id']
        )


def downgrade():
    # Revert invoices table
    with op.batch_alter_table(
        'invoices',
        naming_convention={
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
        }
    ) as batch_op:
        batch_op.drop_constraint(
            'fk_invoices_sale_id_customer_history',
            type_='foreignkey'
        )
        batch_op.drop_column('sale_id')
        batch_op.drop_column('status')
        batch_op.drop_column('amount_paid')
        batch_op.drop_column('total')

    # Revert audit_logs table
    with op.batch_alter_table(
        'audit_logs',
        naming_convention={
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
        }
    ) as batch_op:
        batch_op.add_column(sa.Column('details', sa.VARCHAR(length=255), nullable=True))
        batch_op.create_foreign_key(
            'fk_audit_logs_user_id_users',
            'users',
            ['user_id'],
            ['id']
        )
        batch_op.drop_constraint('uq_audit_logs_hash', type_='unique')
        batch_op.drop_index('ix_audit_logs_entity_id')
        batch_op.drop_index('ix_audit_logs_entity')
        batch_op.alter_column(
            'created_at',
            existing_type=sa.String(length=40),
            type_=sa.DATETIME(),
            nullable=True
        )
        batch_op.alter_column(
            'user_id',
            existing_type=sa.INTEGER(),
            nullable=False
        )
        batch_op.alter_column(
            'action',
            existing_type=sa.String(length=20),
            type_=sa.VARCHAR(length=50),
            existing_nullable=False
        )
        batch_op.alter_column(
            'entity_id',
            existing_type=sa.INTEGER(),
            nullable=True
        )
        batch_op.alter_column(
            'entity',
            existing_type=sa.String(length=30),
            type_=sa.VARCHAR(length=50),
            existing_nullable=False
        )
        batch_op.drop_column('hash')
        batch_op.drop_column('prev_hash')
        batch_op.drop_column('new_values')
        batch_op.drop_column('old_values')

    # Drop payments table
    op.drop_index('ix_payments_invoice_id', table_name='payments')
    op.drop_table('payments')
