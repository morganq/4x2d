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

def all_nearby(pos, others, range):
    return [o for o in others if (pos - o.pos).sqr_magnitude() < range ** 2]

PI = 3.14159
PI2 = 6.2818
def get_angle_delta(a, b):
    a = (a + PI2) % PI2
    b = (b + PI2) % PI2
    result = b - a
    result = (result + PI) % PI2 - PI
    return result