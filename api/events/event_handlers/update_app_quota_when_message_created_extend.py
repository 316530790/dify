import logging

from sqlalchemy import update
from sqlalchemy.orm import Session

from core.app.entities.app_invoke_entities import (
    AdvancedChatAppGenerateEntity,
    AgentChatAppGenerateEntity,
    ChatAppGenerateEntity,
)
from events.message_event import message_was_created
from extensions.ext_database import db
from models.app_quota_extend import AppQuota
from models.model import Message

logger = logging.getLogger(__name__)


@message_was_created.connect
def handle(sender: Message, **kwargs):
    """
    Handles updating the app quota when a message is created.
    This is an extended feature and operates independently.
    """
    message = sender
    application_generate_entity = kwargs.get("application_generate_entity")

    # 1. Check if we have the necessary context from a standard app run.
    if not isinstance(
        application_generate_entity,
        (
            ChatAppGenerateEntity,
            AgentChatAppGenerateEntity,
            AdvancedChatAppGenerateEntity,
        ),
    ):
        return

    # 2. Get the app_id and calculate the token usage.
    app_id = application_generate_entity.app_config.app_id
    tokens_used = (message.message_tokens or 0) + (message.answer_tokens or 0)

    if not app_id or tokens_used == 0:
        return

    try:
        # 3. Perform the database update within a transaction.
        with Session(db.engine) as session:
            # This is an atomic "UPSERT"-like operation.
            # First, try to atomically update the existing record.
            stmt = (
                update(AppQuota)
                .where(AppQuota.app_id == app_id)
                .values(quota_used=AppQuota.quota_used + tokens_used)
                .returning(AppQuota.id)  # Use returning to check if a row was updated
            )

            result = session.execute(stmt)
            updated_row_id = result.scalar_one_or_none()

            # If no row was updated, it means the record doesn't exist yet.
            if not updated_row_id:
                # Check again to prevent race conditions where another process created it.
                existing = session.query(AppQuota.id).filter(AppQuota.app_id == app_id).scalar()
                if not existing:
                    logger.info("No AppQuota record found for app_id: %s. Creating a new one.", app_id)
                    new_quota_record = AppQuota(
                        app_id=app_id,
                        quota_limit=0,  # Default limit, can be configured elsewhere.
                        quota_used=tokens_used,
                    )
                    session.add(new_quota_record)

            # The session context manager handles the commit.
            session.commit()

        logger.info(
            "Successfully updated quota for app %s. Used: %s, New Total: updated in DB.",
            app_id,
            tokens_used,
        )

    except Exception:
        logger.exception("Failed to update app quota for app_id: %s.", app_id)
        # We do not re-raise the exception to avoid breaking the main message creation flow.
        # The quota update is a non-critical, separate plugin logic.
