class BuildOrder:
    def __init__(self, steps):
        self.time = 0
        self.steps = steps

    def is_over(self):
        return len(self.steps) == 0

    def update(self, alien, dt):
        self.time += dt
        if self.is_over():
            return

        pending_step = self.steps[0]
        if self.time > pending_step.time:
            if not pending_step.triggered:
                print("trigger", str(pending_step))
                pending_step.trigger(alien)
            else:
                pending_step.update(alien, dt)
            if pending_step.done:
                print("done with", str(pending_step))
                self.steps.pop(0)
            elif pending_step.abandoned:
                print("abandoning", str(pending_step))
                self.steps.pop(0)                


class BuildOrderStep:
    name = "unimplemented"
    def __init__(self, time):
        self.time = time
        self.triggered = False
        self.done = False
        self.abandoned = False
    
    def trigger(self, alien):
        self.triggered = True

    def update(self, alien, dt):
        pass

class BOAttack(BuildOrderStep):
    name = "attack"
    ATTACK_TYPE_RANDOM = "random"
    ATTACK_TYPE_CENTRAL = "central"
    ATTACK_TYPE_OUTLYING = "outlying"
    def __init__(self, time, attack_type=None):
        super().__init__(time)
        self.attack_type = attack_type or self.ATTACK_TYPE_OUTLYING
        self.duration = 0

    def trigger(self, alien):
        self.done = alien.execute_attack(self.attack_type)
        return super().trigger(alien)

    # Need update in case it was impossible to attack before
    def update(self, alien, dt):
        self.duration += dt
        if self.duration > 20:
            self.abandoned = True
            return        
        if not self.done:
            self.done = alien.execute_attack(self.attack_type)
        return super().update(alien, dt)

    def __str__(self) -> str:
        return "%d: Attack %s" % (self.time, self.attack_type)

class BOExpand(BuildOrderStep):
    name = "expand"
    TARGET_TYPE_NEAR_HOME = "near_home"
    TARGET_TYPE_NEAR_ENEMY = "near_enemy"
    TARGET_TYPE_MIDDLE = "middle"
    TARGET_TYPE_RANDOM = "random"
    def __init__(self, time, target_type=None):
        super().__init__(time)
        self.target_type = target_type or self.TARGET_TYPE_NEAR_HOME
        self.duration = 0

    def __str__(self) -> str:
        return "%d: Expand %s" % (self.time, self.target_type)

    def trigger(self, alien):
        self.done = alien.execute_expand(self.target_type)
        return super().trigger(alien)

    # Need update in case it was impossible to expand before
    def update(self, alien, dt):
        self.duration += dt
        if self.duration > 20:
            self.abandoned = True
            return        
        if not self.done:
            self.done = alien.execute_expand(self.target_type)
        return super().update(alien, dt)

class BOResearch(BuildOrderStep):
    name = "research"
    #TARGET_TYPE_LOW_ASSETS = "low_assets"
    TARGET_TYPE_LACKING_ASSET = "lacking_asset"
    TARGET_TYPE_RANDOM = "random"
    TARGET_TYPE_HOMEWORLD = "homeworld"
    TARGET_TYPE_UNDEFENDED = "undefended"
    def __init__(self, time, asset, backup=None, target_type=None):
        super().__init__(time)
        self.duration = 0
        self.target_type = target_type or self.TARGET_TYPE_RANDOM
        self.asset = asset
        self.backup = backup

    def update(self, alien, dt):
        self.duration += dt
        if self.duration > 20:
            if self.backup:
                self.done = alien.execute_research(self.backup, self.target_type)
            if not self.done:
                self.abandoned = True
            return

        self.done = alien.execute_research(self.asset, self.target_type)
        
        return super().update(alien, dt)

    def trigger(self, alien):
        self.done = alien.execute_research(self.asset, self.target_type)
        return super().trigger(alien)

    def __str__(self) -> str:
        return "%d: Research %s" % (self.time, self.asset)
