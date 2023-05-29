import os
import uuid
import flask
import phfetch
import threading
import webbrowser
from time import sleep

app = flask.Flask(__name__, static_folder = 'client/')

# Keep track of the progress of all threads
THREADS: dict[str, str | int] = {}


def download(video: phfetch.video,
             session: str,
             args: dict) -> None:
    '''
    Download one video as a thread.
    '''
    
    path = args.get('path', './output/')
    qual = args.get('qual', 'best')
    
    # Correct path if needed
    if not path.endswith(('/', '\\')): path += '/'
    
    def progress(*args) -> None:
        # Store and display the current progress
        
        if len(args) == 3:
        
            msg, cur, out = args
            THREADS[session] = f'{cur}/{out}'
            print(msg, cur, '/', out)
    
    try:
        video.download(path, qual,
                       callback = progress,
                       escape_stdout = False)

        THREADS[session] = 'done'
    
    except Exception as err:
        
        print('Thread Error:', repr(err))
        THREADS[session] = 'error'
        
        # Delete after short time
        sleep(10)
        del THREADS[session]

@app.route('/')
def home() -> None:
    
    return flask.send_file('client/index.html', mimetype = 'text/html')

@app.route('/get')
def get() -> None:
    '''
    Start a download.
    '''
    
    # Get arguments
    key = flask.request.args.get('key')
    
    # Load the video
    video = phfetch.video(key = key)
    session = uuid.uuid4().hex
    THREADS[session] = 'starting'
    
    # Start the download and return the image url/title
    threading.Thread(target = download,
                     args = [video,
                             session,
                             flask.request.args.to_dict()]).start()
    
    return flask.jsonify({'title': video.title,
                          'thumbnail': video.image,
                          'session': session})

@app.route('/state')
def state() -> None:
    '''
    Handle sending threads status.
    '''
    
    session = flask.request.args.get('id')
    return THREADS.get(session, 'unknown-thread')

@app.route('/open')
def open_() -> None:
    '''
    Open the video dir.
    '''
    
    print('Opening video')
    
    out = flask.request.args.get('dir', './output/')
    
    files = sorted([out + f for f in os.listdir(out)],
                   key = os.path.getatime)

    if not files: return 'fail', 400
    
    os.startfile(os.path.normpath(os.path.normcase(files[-1])))


if __name__ == '__main__':
    
    # webbrowser.open_new('http://127.0.0.1:5000')
    
    # Note: you can run that for production with gunicorn 
    # or something but i doubt this is really secure as there
    # is no limit rate
    app.run(debug = True, port = 5000)

# EOF