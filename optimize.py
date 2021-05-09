class Memo:
    def __init__(self, result):
        self.result = result
        self.calls = 1

frame_memos = {

}

def frame_memoize(fn):
    frame_memos[fn] = {}
    def wrapped_fn(*args, **kwargs):
        if kwargs:
            raise Exception("Can't memoize kwargs functions")

        # Check if we have these arguments recorded
        ha = hash(args)
        if ha in frame_memos[fn]: # We do
            memo = frame_memos[fn][ha]
            memo.calls += 1
            return memo.result
        else: # We don't
            result = fn(*args)
            frame_memos[fn][ha] = Memo(result)
        return result
    return wrapped_fn

def reset_frame_memos():
    for fn, results in frame_memos.items():
        frame_memos[fn] = {}

def print_memos():
    print(", ".join(["%s:%d/%d" % (str(fn.__name__), len(memos), sum(
        [m.calls for _,m in memos.items()]
    )) for fn, memos in frame_memos.items()]))    