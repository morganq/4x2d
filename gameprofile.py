def dump_stats(profile, total_time):
    print(total_time)
    stats = profile.getstats()
    stats.sort(key=lambda x:x.totaltime, reverse=True)
    for stat in stats[0:20]:
        print("%.2f%%\t(%f)\t" % ((stat.totaltime / total_time * 100), stat.totaltime), stat.code)
    
