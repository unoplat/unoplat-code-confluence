from data_models.chapi_unoplat_position import Position
from pydantic import  Field
from typing import Optional

from data_models.dspy.dspy_unoplat_fs_annotation_subset import DspyUnoplatAnnotationSubset


class Annotation(DspyUnoplatAnnotationSubset):
    position: Optional[Position] = Field(default=None, alias="Position")
