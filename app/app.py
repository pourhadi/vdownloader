from flask import Flask
from flask import request
from flask import send_from_directory
import subprocess
from subprocess import Popen
import uuid
import os
import asyncio
from pathlib import Path
import redis
import shutil

app = Flask(__name__)
app.use_x_sendfile = True

this_dir = os.path.dirname(os.path.realpath(__file__))

# dir = '/videos'
dir = this_dir

cache = redis.Redis(host='redis', port=6379)

@app.route('/', methods=['POST', 'GET'])
def root():
    if request.method == 'POST':
        url = request.form['url']
        downloadID = str(uuid.uuid1())

        print(downloadID)
        # subprocess.call(["youtube-dl", "-f", "bestvideo[height<=480]+bestaudio/best[height<=480]", "--recode-video", "mp4", "-o", downloadID, url], cwd=dir)
        # p = Popen(["youtube-dl", "--hls-prefer-ffmpeg", "--http-chunk-size", "1M", "-f", "bestvideo[height<=480]+bestaudio/best[height<=480]", "-o", downloadID, url], cwd=dir)

        p = Popen(["python3", os.path.join(os.path.dirname(os.path.realpath(__file__)), "downloader.py"), url, downloadID])
        # for path in Path(dir).iterdir():
        #
        #     if id in path.name:
        #         info = path.stat()
        #         print(info)


        cache.set(downloadID, '0')
        # asyncio.run(run("youtube-dl -f 'bestvideo[height<=480]+bestaudio/best[height<=480]' --recode-video=mp4 -o '{}' '{}'".format(downloadID, url)))

        return downloadID


@app.route('/get', methods=['POST', 'GET'])
def get():
    if request.method == 'POST':
        id = request.form['file']

        outputString = ''
        # for path in Path(dir).iterdir():
        #
        #     if id in path.name:
        #         info = path.stat()
        #         print(info)

        for file in os.listdir(dir):
            # print(file)
            if id in file:
                print('downloadID in file')
                outputString = file

        print(os.path.join(dir, outputString))

        return send_from_directory(dir, outputString, as_attachment=True)
        # return send_file(os.path.join(dir, outputString))


@app.route('/check', methods=['POST', 'GET'])
def check():
    print('check')
    if request.method == 'POST':
        name = request.form['file']
        print(name)
        status = (cache.get(name)).decode('utf8')
        print(status)
        if 'done' in status:
            finished_file = None
            for file in os.listdir(dir):
                if name in file:
                    if '.mkv' in file:
                        finished_file = file

                    if '.mp4' in file:
                        finished_file = file

                    if '.mov' in file:
                        finished_file = file

                    if '.' not in file:
                        finished_file = file

            if finished_file is not None:
                print("finished_file")
                # shutil.move(os.path.join(this_dir, finished_file), os.path.join(dir, finished_file))
                cache.set(name, finished_file)
                return finished_file

            return status
        else:
            return status

        outputString = ''
        # dir = os.path.abspath(os.path.dirname(sys.argv[0]))

        # for path in Path(dir).iterdir():
        #     print(path.name)
        #     if id in path.name:
        #         info = path.stat()
        #         print(info)

        count = 0
        for file in os.listdir(dir):
            if id in file:
                # print(os.stat(os.path.join(dir, file)))
                count = count + 1

        if count > 1:
            return ''

        if count == 0:
            return "FAIL"

        for file in os.listdir(dir):
            if id in file:
                if '.mkv' in file:
                    return file

                if '.mp4' in file:
                    return file

                if '.mov' in file:
                    return file

                if '.' not in file:
                    return file

        return ''


@app.route('/done', methods=['POST', 'GET'])
def done():
    if request.method == 'POST':
        id = request.form['id']



# if __name__ == '__main__':
#     app.run()


if __name__ == "__main__":
    reactor_args = {}

    print("starting up")
    def run_twisted_wsgi():
        from twisted.internet import reactor
        from twisted.web.server import Site
        from twisted.web.wsgi import WSGIResource
        from twisted.web.static import File
        from twisted.internet import endpoints
        from twisted.web.resource import Resource
        from twisted.web import server, static

        top_resource = Resource()
        resource = WSGIResource(reactor, reactor.getThreadPool(), app)

        top_resource.putChild(b'app', resource)
        top_resource.putChild(b'files', static.File(dir))

        site = Site(top_resource)
        reactor.listenTCP(5000, site)

        reactor.run(**reactor_args)


    # if app.debug:
    #     # Disable twisted signal handlers in development only.
    #     reactor_args['installSignalHandlers'] = 0
    #     # Turn on auto reload.
    #     import werkzeug.serving
    #
    #     run_twisted_wsgi = werkzeug.serving.run_with_reloader(run_twisted_wsgi)

    run_twisted_wsgi()