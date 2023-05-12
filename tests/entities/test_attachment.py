from typing import Any

from signalation.entities.attachment import AttachmentFile


def test_attachment_file_encoding_and_decoding_works_as_expected(test_attachment_file_dict: dict[str, Any]):
    # encoding happens during validation (`bytes_to_str`)
    attachment_file = AttachmentFile.parse_obj(test_attachment_file_dict)
    # decoding happens in `attachment_bytes` property
    assert attachment_file.attachment_bytes == test_attachment_file_dict["attachment_bytes_str"]
