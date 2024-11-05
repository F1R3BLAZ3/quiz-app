from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = 'ab5370197694'
down_revision = 'bf5306167699'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    # Update existing records to set default JSON values using text()
    conn.execute(text("UPDATE quiz_result SET user_answers = '[]' WHERE user_answers IS NULL;"))
    conn.execute(text("UPDATE quiz_result SET question_ids = '[]' WHERE question_ids IS NULL;"))

def downgrade():
    conn = op.get_bind()
    # Optionally revert back if necessary
    conn.execute(text("UPDATE quiz_result SET user_answers = NULL WHERE user_answers = '[]';"))
    conn.execute(text("UPDATE quiz_result SET question_ids = NULL WHERE question_ids = '[]';"))
