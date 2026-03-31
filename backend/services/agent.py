import re
class StitchFlowAgent:
    def parse_command(self, text):
        """
        Simple NLP backbone.
        Example: 'New order for koffi,
        chest 42, length 55'
        """
        text = text.lower()
        chest = re.search(r'chest (\d+)',text)
        length = re.search(r'length (\d+)', text)
        name = re.search(r'for (\w+)', text)

        return{
            "customer": name.group(1) if name else "unknown",
            "measurements":{
                "chest": chest.group(1) if chest else None, 
                "length": length.group(1) if length else None
            },
            "intent": "new_order" if "new" in text else "query"
        }