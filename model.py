from dataclasses import dataclass


@dataclass
class Rate:
    user: str
    date: str
    kind: str
    value: int


@dataclass
class Question:
    kind: str
    bad_description: str
    good_description: str

