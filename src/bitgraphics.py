import json

class BitGraphic:
    def __init__(self) -> None:
        self.bits:list[bool] = []
        self.width:int = 0
        self.height:int = 0

    def to_json(self) -> str:
        ToReturn = {"bits": self.bits, "width": self.width, "height": self.height}
        return json.dumps(ToReturn)
    

bg = BitGraphic()
bg.bits = [False, True, False, True]
bg.width = 200
bg.height = 100
print(bg.to_json())