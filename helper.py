def clamp(x, a, b):
    return min(max(x,a),b)

def nearest_order(pos, others):
    return sorted(others, key = lambda x:(x.pos - pos).sqr_magnitude())

def get_nearest(pos, others):
    dist = 999999999
    res = None
    for other in others:
        delta = (other.pos - pos).sqr_magnitude()
        if delta < dist:
            dist = delta
            res = other
    return res, dist