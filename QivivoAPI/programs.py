class Programs:
    api = None
    user_active_program_id = None
    user_programs = []

    def __init__(self, device):
        self.device = device
        return


class Program:
    id = None
    name = None
    program = {'monday': [],
               'tuesday': [],
               'wednesday': [],
               'thursday': [],
               'friday': [],
               'saturday': [],
               'sunday': []}

    def __init__(self):
        return


class Period:
    period_start = "00:00"
    period_end = "23:59"
    temperature_setting = None

    def __init__(self, start="00:00", end="23:00", setting='night_temperature'):
        self.period_start = start
        self.period_end = end
        self.temperature_setting = setting
        return
