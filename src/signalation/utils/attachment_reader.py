import io
import json
from pathlib import Path

from PIL import Image

from signalation.entities.signal import AttachmentFile


class AttachmentReader:
    def __init__(self, topic_path: Path) -> None:
        self.topic_path = topic_path
        self.attachment_file = AttachmentReader._get_attachment_file(topic_path)
        if self.attachment_file.attachment.contentType == "image/png":
            self.recreated_attachment = AttachmentReader.create_img(self.attachment_file)

    @staticmethod
    def create_img(attachment_file: AttachmentFile, show: bool = True):
        imageStream = io.BytesIO(attachment_file.attachment_bytes)
        imageFile = Image.open(imageStream)
        if show:
            imageFile.show()
        return imageFile

    @staticmethod
    def _get_attachment_file(topic_path: Path) -> AttachmentFile:
        with open(topic_path) as f:
            topic_data = f.read()
        topic_data_dict = json.loads(topic_data)
        attachment_data_dict = json.loads(topic_data_dict["Content"])
        attachment_file = AttachmentFile.parse_obj(attachment_data_dict)
        return attachment_file
