from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Tuple

@dataclass
class Box:
    """Detection rect"""
    xc: float
    yc: float
    w: float
    h: float

    @classmethod
    def from_tuple(cls, box: Tuple[float, float, float, float]) -> 'Box':
        return Box(xc=float(box[0]), yc=float(box[1]), w=float(box[2]), h=float(box[3]))

    def left(self) -> float:
        return self.xc - self.w * 0.5

    def right(self) -> float:
        return self.xc + self.w * 0.5

    def top(self) -> float:
        return self.yc - self.h * 0.5

    def bottom(self) -> float:
        return self.yc + self.h * 0.5

    def calc_iou(self, other: 'Box') -> float:
        """Calculates intersection over union ration which can be used to compare boxes"""
        al = self.left()
        ar = self.right()
        at = self.top()
        ab = self.bottom()

        bl = other.left()
        br = other.right()
        bt = other.top()
        bb = other.bottom()

        i_l = max(al, bl)
        i_r = min(ar, br)
        i_t = max(at, bt)
        i_b = min(ab, bb)

        o_l = min(al, bl)
        o_r = max(ar, br)
        o_t = min(at, bt)
        o_b = max(ab, bb)

        i_w = i_r - i_l
        i_h = i_b - i_t
        o_w = o_r - o_l
        o_h = o_b - o_t

        o_a = o_w * o_h
        if o_a <= 0.0:
            return 0.0
        return i_w * i_h / o_a


@dataclass
class Detection:
    """Detection result"""
    name: str
    confidence: float
    box: Box

    @classmethod
    def from_tuple_list(cls, detections: List[Tuple[str, float, Tuple[float, float, float, float]]]) -> List['Detection']:
        return [Detection.from_tuple(d) for d in detections]

    @classmethod
    def from_tuple(cls, detection: Tuple[str, float, Tuple[float, float, float, float]]) -> 'Detection':
        box = Box.from_tuple(detection[2])
        return Detection(detection[0], float(detection[1]), box)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Detection':
        return Detection(data['name'], data['confidence'], Box(**data['box']))



def compare_detections(l1: List[Detection], l2: List[Detection], threshold: float = 0.4) -> bool:
    """Compares two lists of detections. Returns true if lists looks similar with some threshold"""

    # Are there all boxes from l1 matching any in l2
    for a in l1:
        found = False
        for b in l2:
            iou = a.box.calc_iou(b.box)
            if iou >= threshold:
                found = True
                break
        if not found:
            return False

    # are there all boxes in l2 matching any in l1
    # the list may differ and contain duplicates,
    # that's why we need two checks
    for b in l2:
        found = False
        for a in l1:
            iou = a.box.calc_iou(b.box)
            if iou >= threshold:
                found = True
                break
        if not found:
            return False

    return True

