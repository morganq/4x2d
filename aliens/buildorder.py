class BuildOrder:
    def __init__(self, steps):
        self.steps = steps
        self.step_index = 0

    def is_over(self):
        return self.step_index >= len(self.steps)

    def get_current_step(self, time):
        if self.step_index >= len(self.steps):
            return None
        step = self.steps[self.step_index]
        if time < step.time:
            return None
        elif time > step.time + 60:
            print("Skipping", step)
            self.step_index += 1
            return self.get_current_step(time)
        else:
            return step

    def completed_current_step(self):
        if self.step_index < len(self.steps):
            step = self.steps[self.step_index]
            print("Completed", step)
            self.step_index += 1


class BuildOrderStep:
    name = "unimplemented"
    def __init__(self, time):
        self.time = time

class BOAttack(BuildOrderStep):
    name = "attack"
    def __init__(self, time, target_type=None):
        super().__init__(time)
        self.target_type = target_type

    def __str__(self) -> str:
        return "%d: Attack %s" % (self.time, self.target_type)

class BOExpand(BuildOrderStep):
    name = "expand"
    TARGET_TYPE_NEAR_HOME = "near_home"
    TARGET_TYPE_NEAR_ENEMY = "near_enemy"
    TARGET_TYPE_MIDDLE = "middle"
    TARGET_TYPE_RANDOM = "random"
    def __init__(self, time, target_type=None):
        super().__init__(time)
        self.target_type = target_type

    def __str__(self) -> str:
        return "%d: Expand %s" % (self.time, self.target_type)

class BOResearch(BuildOrderStep):
    name = "research"
    def __init__(self, time, asset):
        super().__init__(time)
        self.asset = asset

    def __str__(self) -> str:
        return "%d: Research %s" % (self.time, self.asset)
