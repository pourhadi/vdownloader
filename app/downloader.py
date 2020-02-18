import youtube_dl
import sys
import redis
import shutil
import os

this_dir = os.path.dirname(os.path.realpath(__file__))

url = sys.argv[1]
id = sys.argv[2]

# p = Popen(["youtube-dl", "--hls-prefer-ffmpeg", "--http-chunk-size", "1M", "-f",
#            "bestvideo[height<=480]+bestaudio/best[height<=480]", "-o", downloadID, url], cwd=dir)

r = redis.Redis(host='redis', port=6379)

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    # print(d)
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
    elif d['status'] == 'error':
        r.set(id, "error")
    else:
        total = None
        try:
            if d['total_bytes_estimate'] is not None:
                total = d['total_bytes_estimate']
        except:
            print('no bytes estimate')

        try:
            if d['total_bytes'] is not None:
                total = d['total_bytes']

        except:
            print('no total bytes')

        if total is not None:
            downloaded = d['downloaded_bytes']
            percent = int((downloaded / total) * 100)
            # print('set: {} - {}'.format(id, percent))
            r.set(id, str(percent))



ydl_opts = {
    'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
    'logger': MyLogger(),
    'outtmpl': id,
    'progress_hooks': [my_hook],
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

    found = False
    for file in os.listdir('/'):
        # print(file)
        if id in file:
            shutil.move(os.path.join('/', file), os.path.join('/videos', file))
            r.set(id + "_file", file)
            r.set(id, "done")
            found = True
            break

    if not found:
        r.set(id, "error")
