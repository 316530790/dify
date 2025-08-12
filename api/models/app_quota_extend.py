from sqlalchemy.dialects.postgresql import UUID

from extensions.ext_database import db


class AppQuota(db.Model):
    """
    Represents the quota information for an application.
    This table stores usage limits and tracking for each app.
    The 'Ext' suffix in the class name is for English extension identifier as requested.
    """
    __tablename__ = 'app_quota_extend'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='app_quota_pkey'),
        db.Index('app_quota_app_id_idx', 'app_id'),
    )

    # 额度记录的唯一标识符
    id = db.Column(UUID, primary_key=True, server_default=db.text('uuid_generate_v4()'))
    # 关联的应用ID (普通字段，无外键)
    app_id = db.Column(UUID, nullable=False)
    # 配额上限
    quota_limit = db.Column(db.Integer, nullable=False, server_default=db.text('0'))
    # 已使用的配额
    quota_used = db.Column(db.Integer, nullable=False, server_default=db.text('0'))
    # 上次重置时间
    last_reset_at = db.Column(db.DateTime)
    # 创建时间
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    # 最后更新时间
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    def to_dict(self):
        return {
            'id': str(self.id),
            'app_id': str(self.app_id),
            'quota_limit': self.quota_limit,
            'quota_used': self.quota_used,
            'last_reset_at': self.last_reset_at.isoformat() if self.last_reset_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
