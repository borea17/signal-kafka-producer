"""Signal object definitions as defined from `bbernhard/signal-cli-rest-api`."""

from typing import Literal, Optional
from uuid import UUID

import pandas as pd
from pydantic import BaseModel


class Attachment(BaseModel):
    content_type: str
    filename: str
    id: str
    size: int


class GroupInfo(BaseModel):
    groupID: str
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
    attachments: Optional[list[Attachment]] = None
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
    message: str
    expiresInSeconds: int
    viewOnce: bool
    groupInfo: Optional[GroupInfo] = None


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
    def timestamp(self) -> int:
        """Utility to get associated timestamp"""
        if type(self.envelope.syncMessage) == SyncMessage:
            timestamp_epoch = self.envelope.syncMessage.sentMessage.timestamp
        elif type(self.envelope.dataMessage) == DataMessage:
            timestamp_epoch = self.envelope.dataMessage.timestamp
        else:
            timestamp_epoch = 0
        return pd.to_datetime(timestamp_epoch * 1000000)
