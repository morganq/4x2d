import math
class V2:
    """A two-dimensional vector with Cartesian coordinates."""

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):
        """Human-readable string representation of the vector."""
        return '({:g},{:g})'.format(self.x, self.y)

    def __repr__(self):
        """Unambiguous string representation of the vector."""
        return repr((self.x, self.y))

    def dot(self, other):
        """The scalar (dot) product of self and other. Both must be vectors."""

        if not isinstance(other, V2):
            raise TypeError('Can only take dot product of two V2 objects')
        return self.x * other.x + self.y * other.y
    # Alias the __matmul__ method to dot so we can use a @ b as well as a.dot(b).
    __matmul__ = dot

    def cross(self, other):
        return self.x * other.y - self.y * other.x

    def __sub__(self, other):
        """Vector subtraction."""
        return V2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        """Vector addition."""
        return V2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        """Multiplication of a vector by a scalar."""

        if isinstance(scalar, int) or isinstance(scalar, float):
            return V2(self.x*scalar, self.y*scalar)
        raise NotImplementedError('Can only multiply V2 by a scalar')

    def __rmul__(self, scalar):
        """Reflected multiplication so vector * scalar also works."""
        return self.__mul__(scalar)

    def __neg__(self):
        """Negation of the vector (invert through origin.)"""
        return V2(-self.x, -self.y)

    def __truediv__(self, scalar):
        """True division of the vector by a scalar."""
        return V2(self.x / scalar, self.y / scalar)

    def __mod__(self, scalar):
        """One way to implement modulus operation: for each component."""
        return V2(self.x % scalar, self.y % scalar)

    def __abs__(self):
        """Absolute value (magnitude) of the vector."""
        return math.sqrt(self.x**2 + self.y**2)

    def distance_to(self, other):
        """The distance between vectors self and other."""
        return abs(self - other)

    def to_polar(self):
        """Return the vector's components in polar coordinates."""
        return self.__abs__(), math.atan2(self.y, self.x)

    def magnitude(self):
        return abs(self)

    def sqr_magnitude(self):
        return self.x ** 2 + self.y ** 2

    def normalized(self):
        if self.x == 0 and self.y == 0:
            return V2(0,0)        
        d = self.magnitude()
        return V2(self.x / d, self.y / d)

    def tuple(self):
        return (self.x, self.y)

    def tuple_int(self):
        return (int(self.x), int(self.y))

    def max(self, max_mag):
        if self.sqr_magnitude() > max_mag ** 2:
            return self.normalized() * max_mag
        else:
            return self

    def copy(self):
        return V2(self.x, self.y)

    @staticmethod
    def from_angle(angle):
        return V2(math.cos(angle), math.sin(angle))