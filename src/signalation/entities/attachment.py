import base64
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, validator

from signalation.entities.signal_message import Attachment


class AttachmentMetaData(BaseModel):
    chat_name: str
    sender: str
    timestamp_epoch: int
    attachment: Attachment
    attachment_dir: Path

    @property
    def file_basename(self) -> str:
        return f"{self.timestamp}_{self.attachment.size}"

    @property
    def raw_file_path(self) -> Path:
        raw_file_dir = self.attachment_dir / "raw" / self.chat_name
        raw_file_dir.mkdir(parents=True, exist_ok=True)
        return raw_file_dir / f"{self.file_basename}.json"

    @property
    def actual_file_path(self) -> Path:
        actual_file_dir = self.attachment_dir / self.chat_name
        actual_file_dir.mkdir(parents=True, exist_ok=True)

        file_ending = self.attachment.contentType.split("/")[-1]
        return actual_file_dir / f"{self.file_basename}.{file_ending}"

    @property
    def timestamp(self) -> pd.Timestamp:
        return pd.to_datetime(self.timestamp_epoch * 1000000)


class AttachmentFile(AttachmentMetaData):
    attachment_bytes_str: str
    """Attachment bytes represented in a string.

    Notes:
        - input to this field can be bytes or string (pydantic validator takes care of encoding)
        - we don't want to store raw bytes here, since these are not json-serializable
    """

    @validator("attachment_bytes_str", always=True, pre=True)
    def bytes_to_str(cls, attachment_byte_or_str: bytes | str) -> str:
        if type(attachment_byte_or_str) == bytes:
            attachment_byte_or_str = base64.b64encode(attachment_byte_or_str).decode("ascii")
        return attachment_byte_or_str

    @property
    def attachment_bytes(self) -> bytes:
        return base64.b64decode(self.attachment_bytes_str)

    @property
    def meta_data_dict(self) -> dict:
        meta_data = AttachmentMetaData(
            chat_name=self.chat_name,
            sender=self.sender,
            timestamp_epoch=self.timestamp_epoch,
            attachment=self.attachment,
            attachment_dir=self.attachment_dir,
        )
        meta_data_dict = meta_data.dict()
        # add some usefule properties here
        meta_data_dict["raw_file_path"] = self.raw_file_path
        meta_data_dict["actual_file_path"] = self.actual_file_path
        return meta_data_dict
