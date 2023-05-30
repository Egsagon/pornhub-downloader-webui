import os
import uuid
import flask
import phfetch
import threading
from time import sleep
from dataclasses import dataclass

app = flask.Flask(__name__, static_folder = 'client/')


@dataclass
class Request:
    session: str
    video: phfetch.video
    quality: str | int
    filepath: str
    progress: int = 0
    status: str = 'in queue...'
    
    def get_status(self) -> dict:
        '''
        Get status to send to the client.
        '''
        
        return {'progress': self.progress,
                'status': self.status,
                'filepath': self.filepath}

class Worker:
    def __init__(self, wid: int) -> None:
        '''
        Represents an instance of a worker that can
        download one video at a time.
        '''
        
        self.id = wid
        self.running = False
        self.queue: list[Request] = []
    
    def run(self) -> None:
        '''
        Start the worker.
        '''
        
        self.running = True
        while self.running:
            
            # Get the first queue element
            sleep(.5)
            if not len(self.queue): continue
            request = self.queue.pop(0)
            
            # Download the video
            def log(txt, cur = 0, total = None) -> None:
                # Update the request status
                # every segment download
                
                print(f'[W-{self.id}]', txt, cur, '/', total)
                
                if total is None: return # wait for the real download
                request.progress = round((int(cur) / int(total)) * 100)
            
            request.status = 'Downloading'
            
            request.video.download(
                path = request.filepath,
                quality = request.quality,
                callback = log
            )
            
            # End
            request.progress = 100
            request.status = 'done'
            
            # Delete the file in 1 hour
            def delete() -> None:
                print(f'Deleting old ressource {request.filepath}')
                os.remove(request.filepath)
            
            threading.Timer(30, delete).start()
    
    def start(self) -> None:
        '''
        Start the worker in a thread.
        '''
        
        threading.Thread(target = self.run).start()

    def stop(self) -> None:
        '''
        Stop the worker after the end of the current loop.
        '''
        
        self.running = False


WORKER_COUNT = 5
WORKERS: list[Worker] = []
SESSIONS: dict[str, Request] = {}


@app.route('/')
def home() -> None:
    '''
    Send main page.
    '''
    
    return flask.send_file('client/index.html', mimetype = 'text/html')

@app.route('/get')
def get() -> None:
    '''
    Assign a download to a worker.
    '''
    
    # Get arguments
    key = flask.request.args.get('key')
    qual = flask.request.args.get('qual')
    
    try:
        session = uuid.uuid4().hex
        video = phfetch.video(key = key)
        
        package = Request(session, video, qual, f'./client/output/{session}.mp4')
        
        # Find the least charged worker
        worker = None
        for worker_ in WORKERS:
            
            if worker is None or len(worker_.queue) < len(worker.queue):
                worker = worker_
        
        # Assign the package to the worker and register it
        # to the sessions table
        SESSIONS[session] = package
        worker.queue.append(package)
        
    except Exception as err:
        
        print(repr(err))
        return flask.jsonify({'error': repr(err)}), 400

    # Send video infos and session id
    return flask.jsonify({'thumbnail': video.image,
                          'title': video.title,
                          'session': session})

@app.route('/status')
def status() -> None:
    '''
    Handle sending current request status.
    '''
    
    session = flask.request.args.get('id', '')
    request = SESSIONS.get(session)
    
    # Return the session status
    if not request: return 'Session not found', 404
    return flask.jsonify(request.get_status())

# Start the workers
for i in range(WORKER_COUNT):
    w = Worker(i)
    WORKERS.append(w)
    w.start()
    
print(f'Started {WORKER_COUNT} workers!')


if __name__ == '__main__':
    app.run(debug = True, port = 5000)

# EOF