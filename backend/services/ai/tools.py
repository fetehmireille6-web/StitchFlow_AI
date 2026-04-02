def calculate_fabric(skirt_vol, layers, bodice_area):
    """The formula:
    (Skirt_Volume*Layer_Count)+Bodice_Area
    """
    try:
        total = (float(skirt_vol)*float(layers))+float(bodice_area)
        return round(total, 2)
    except ValueError:
        return 0
    
def get_deadline_alert(orders):
    """Simple logic to check if something is due tomorrowx"""
    #placeholder: in a real app, we'd compare dates
    return "Chef, you have 3 fittings today!"