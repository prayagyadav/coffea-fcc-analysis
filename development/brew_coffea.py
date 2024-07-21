import os
import time
from threading import Thread
class brew_coffea():
    def __init__(self):
        self.done = True
        self._thread = Thread(target=self._animateframes, daemon=True)

    def start(self):
        self._thread.start()
        return self

    def __enter__(self):
        self.start()

    def _animate(self):
        while self.done:
            print("Brewing your coffea .")
            time.sleep(1)
            print("Brewing your coffea ..")
            time.sleep(1)
            print("Brewing your coffea ...")
            time.sleep(1)
    def _animateframes(self):
        def print_update(s,**kwargs):
            return print(f"\r{s}", flush=True, **kwargs)

        frame1_text = '''
________________________
|        )  (          |
|        (   ) (       |
|         ) (   )      |
|       _________      |
|    .-'---------|     |
|   (  | COFFEA  |     |
|    '-.---------|     |
|      '_________'     |
|       '-------'      |
|Brewing your coffea.  |
________________________
'''
        frame2_text = '''
________________________
|         (  (         |
|        )  (  (       |
|         (   ) )      |
|       _________      |
|    .-'---------|     |
|   (  | COFFEA  |     |
|    '-.---------|     |
|      '_________'     |
|       '-------'      |
|Brewing your coffea.. |
________________________
'''
        frame3_text = '''
________________________
|               )      |
|        )   ) (       |
|       (   (   )      |
|       _________      |
|    .-'---------|     |
|   (  | COFFEA  |     |
|    '-.---------|     |
|      '_________'     |
|       '-------'      |
|Brewing your coffea...|
________________________
'''

        frames = [frame1_text, frame2_text, frame3_text]
        time_sec = 1
        u = '\033[A'
        print()
        while self.done:
            nlines=len(frames[0].strip().split('\n'))
            #First Frame
            for line in frames[0].strip().split('\n'):
                print_update(line)
            time.sleep(time_sec)

            #Rest of the Frames
            for i,frame in enumerate(frames):
                if i == 0:
                    continue
                for j,line in enumerate(frame.strip().split('\n')):
                    if j == 0:
                        print_update(u*nlines+line)
                    else:
                        print_update(line)
                time.sleep(time_sec)
            print_update(u*nlines,end="")
        print()
 
    def stop(self):
        self.done = False
    def __exit__(self, *args):
        self.stop()
