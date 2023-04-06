"""Signal object definitions as defined from `bbernhard/signal-cli-rest-api`."""

import base64
from typing import Literal, Optional
from uuid import UUID

import pandas as pd
from pydantic import BaseModel, validator


class Attachment(BaseModel):
    contentType: str
    filename: str
    id: str
    size: int


class GroupInfo(BaseModel):
    groupId: str
    type: Literal["DELIVER"]


class Message(BaseModel):
    message: str | None
    # meta info
    destination: str | None
    destinationNumber: str | None
    destinationUuid: UUID | None
    timestamp: int
    viewOnce: bool
    expiresInSeconds: int
    attachments: Optional[list[Attachment]] = []
    groupInfo: GroupInfo | None


class SyncMessageType(BaseModel):
    type: Literal["CONTACTS_SYNC"]


class ReadMessage(BaseModel):
    sender: str
    senderNumber: str
    senderUuid: UUID
    timestamp: int


class SyncMessageReadMessages(BaseModel):
    readMessages: list[ReadMessage]


class SyncMessage(BaseModel):
    sentMessage: Message


class DataMessage(BaseModel):
    timestamp: int
    message: str | None
    expiresInSeconds: int
    viewOnce: bool
    groupInfo: Optional[GroupInfo] = None
    attachments: Optional[list[Attachment]] = []


class SignalEnvelope(BaseModel):
    source: str
    sourceNumber: str
    sourceUuid: UUID
    sourceName: str
    sourceDevice: int
    timestamp: int

    dataMessage: Optional[DataMessage] = None
    syncMessage: Optional[SyncMessage | SyncMessageType | SyncMessageReadMessages] = None


class SignalMessage(BaseModel):
    envelope: SignalEnvelope
    account: str

    @property
    def relevant_for_kafka(self) -> bool:
        """Utility to determine whether the message should be produced to kafka."""
        if (
            type(self.envelope.syncMessage) == SyncMessage
            or type(self.envelope.dataMessage) == DataMessage
        ):
            return True
        else:
            return False

    @property
    def attachments(self) -> list[Attachment]:
        if type(self.envelope.syncMessage) == SyncMessage:
            return self.envelope.syncMessage.sentMessage.attachments
        elif type(self.envelope.dataMessage) == DataMessage:
            return self.envelope.dataMessage.attachments
        else:
            return []

    @property
    def has_attachment(self) -> bool:
        """Whether there is an associated attachment."""
        return len(self.attachments) > 0

    @property
    def chat_name(self) -> str:
        """Utitlity to return the contact/group with whom the message is shared."""
        if type(self.envelope.syncMessage) == SyncMessage:
            if self.envelope.syncMessage.sentMessage.destinationNumber == self.account:
                return "Note to Self"
            else:
                if self.envelope.syncMessage.sentMessage.destinationNumber is not None:
                    return self.envelope.syncMessage.sentMessage.destinationNumber
                else:
                    return self.envelope.syncMessage.sentMessage.groupInfo.groupID
        elif type(self.envelope.dataMessage) == DataMessage:
            return self.envelope.sourceNumber
        else:
            raise NotImplementedError

    @property
    def msg_sender(self) -> str:
        """Utility to return who sent the message."""
        return self.envelope.sourceName

    @property
    def msg_content(self) -> str:
        """Utility to return message content"""
        if type(self.envelope.syncMessage) == SyncMessage:
            return self.envelope.syncMessage.sentMessage.message
        elif type(self.envelope.dataMessage) == DataMessage:
            return self.envelope.dataMessage.message
        else:
            return ""

    @property
    def timestamp(self) -> pd.Timestamp:
        """Utility to get associated timestamp"""
        if type(self.envelope.syncMessage) == SyncMessage:
            timestamp_epoch = self.envelope.syncMessage.sentMessage.timestamp
        elif type(self.envelope.dataMessage) == DataMessage:
            timestamp_epoch = self.envelope.dataMessage.timestamp
        else:
            timestamp_epoch = 0
        return pd.to_datetime(timestamp_epoch * 1000000)


class AttachmentFile(BaseModel):

    attachment_bytes_str: str
    chat_name: str
    sender: str
    timestamp_epoch: int
    attachment: Attachment

    @validator("attachment_bytes_str", always=True, pre=True)
    def bytes_to_str(cls, attachment_byte_or_str: bytes | str) -> str:
        if type(attachment_byte_or_str) == bytes:
            attachment_byte_or_str = base64.b64encode(attachment_byte_or_str).decode("ascii")
        return attachment_byte_or_str

    @property
    def attachment_bytes(self) -> bytes:
        return base64.b64decode(self.attachment_bytes_str)

    @property
    def timestamp(self) -> pd.Timestamp:
        return pd.to_datetime(self.timestamp_epoch * 1000000)
