from dataclasses import dataclass


@dataclass
class AOTexture:
    name: str = ""
    owner_name: str = ""
    type: str = "ao"

@dataclass
class PaintTexture:
    name: str = ""
    owner_name: str = ""
    is_color: bool = False
    type: str = "paint"
    

