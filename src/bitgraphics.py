import json

class BitGraphic:
    def __init__(self) -> None:
        self.bits:list[bool] = []
        self.width:int = 0
        self.height:int = 0

    def to_json(self) -> str:

        # assemble bits as 1's and 0's
        bitsbin:str = ""
        for bit in self.bits:
            if bit:
                bitsbin = bitsbin + "1"
            else:
                bitsbin = bitsbin + "0"

        ToReturn = {"bits": bitsbin, "width": self.width, "height": self.height}
        return json.dumps(ToReturn)
    
    def from_json(self, jsons:str) -> None:

        obj = json.loads(jsons)

        # deserialize bits
        self.bits.clear()
        for c in obj["bits"]:
            if c == "0":
                self.bits.append(False)
            elif c == "1":
                self.bits.append(True)
            else:
                raise Exception("Character '" + c + "' in JSON-serializes 'bits' property is not a valid 0 or 1.")
        
        # width and height
        self.width = obj["width"]
        self.height = obj["height"]
    
    def from_file(self, path:str) -> None:
        f = open(path, "r")
        txt:str = f.read()
        self.from_json(txt)