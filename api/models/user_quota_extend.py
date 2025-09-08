from sqlalchemy import BigInteger

from extensions.ext_database import db


class UserQuota(db.Model):
    """
    Represents the quota information for a user.
    This table stores usage limits and tracking for each user.
    """
    __tablename__ = 'user_quota_extend'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='user_quotas_pkey'),
    )

    id = db.Column(BigInteger, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    quota_limit = db.Column(db.Integer, nullable=False)
    quota_used = db.Column(db.Integer, nullable=False, server_default=db.text('0'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quota_limit': self.quota_limit,
            'quota_used': self.quota_used,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
