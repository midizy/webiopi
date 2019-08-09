import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

PAGE="""\
<html>
	<head>
        <meta charset=utf-8 />
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="viewport" content = "height = device-height, width = device-width, user-scalable = no" />
        <meta name="description" content="description">
        <title>IZY HOUSE</title>
        <link rel="stylesheet" media="screen" href="style1.css" />
        <link href="https://fonts.googleapis.com/css?family=Patrick+Hand" rel="stylesheet">
 
<!--[if IE]>
<script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
<![endif]-->
</head>
	<style>
body {
    background-color:rgb(167, 224, 247);
    background-repeat:no-repeat;
    background-position:center;
    background-size:cover;
    color: #29595f;
  }
  
  .logo {
  height: 130px;
  width: 130px;
  margin-top: 0px;
  margin-left: 130px;
  }
  
  
  .menu{
    padding: 0;
    width: auto;
    height: 30px;
    margin-left: 90px;
    }
      
    .menu ul{ 
      list-style: none;
      }
  
      .menu li{ 
        display: inline;
        float: left;
        padding:0px;
        border-left: #666666 thin solid;
        }
  
        .menu a{
          display: block;
          text-decoration: none;
          padding: 10px;
          background-color: rgb(147, 175, 235);
          font-family:Verdana, Arial, Helvetica, sans-serif;
          font-size: 15px;
          font-weight: bold;
          }                     
                  
          .menu :hover{
            background-color: rgb(174, 198, 243);
            text-decoration: none;
            color: #FFFFFF;
            }
              .menu li.btnesquerdo{
              border: none;}

                button {
        				display: block;
        				text-align: center;
        				text-decoration: none;
        				width: 130px;
                        height: 50px;
                        font-family: 'Amatic SC', cursive;  
                        font-size: 25px;  
                                          		
                        
                        text-shadow: 1px 1px 1px rgba(255,255,255, .22);
        				-webkit-border-radius: 15px;
   						-moz-border-radius: 15px;
    					border-radius: 15px;
 
    					-webkit-box-shadow: 1px 1px 1px rgba(0,0,0, .29), inset 1px 1px 1px rgba(255,255,255, .44);
    					-moz-box-shadow: 1px 1px 1px rgba(0,0,0, .29), inset 1px 1px 1px rgba(255,255,255, .44);
    					box-shadow: 1px 1px 1px rgba(0,0,0, .29), inset 1px 1px 1px rgba(255,255,255, .44);
 
    					-webkit-transition: all 0.15s ease;
    					-moz-transition: all 0.15s ease;
    					-o-transition: all 0.15s ease;
    					-ms-transition: all 0.15s ease;
    					transition: all 0.15s ease;
        				
        				}

 .cam {
border-style: solid;
border-width: 5px;
border-color: DarkSlateGray;
}
     
	</style>
    <body>
	<div>
        <a href="http://192.168.0.202:8000/"> <img class="logo" src="http://192.168.0.202:8000/izyhouse.png"/> </a>
        
      </div>

        <ul class="menu">
        <li class="btnesquerdo"><a href="http://192.168.0.202:8000/Lights/">ILUMINAÇÃO</a></li>
        <li><a href="http://192.168.0.202:5000/index.html">CÂMERA</a></li> 
        </ul></br></br>
        <div><img class="cam" src="stream.mjpg" width="348" height="261"/></div>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 5000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
