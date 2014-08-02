# Copyright (C) John Leach <john@johnleach.co.uk>
# Released under the terms of the GNU General Public License version 3

import BaseHTTPServer
import cgi
import thread
import collections
import itertools

PageInfo = collections.namedtuple('PageInfo', ['title', 'buttons', 'callback', 'actions'])

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        bstr = ""
        bstyle = ""
        info = self.server.page_info
        rows = len(info.buttons)
        bstyle += "button { font-size: 30px; height: %d%%; margin: 0; }" % (int(90 / (rows - 0.1)))
        for r in info.buttons:
            bstr += '<p>'
            for name in r:
                if '#' in name:
                    (name, style) = name.split('#', 1)
                else:
                    style = ''
                bstr += "<button type='submit' name='%s'>%s</button>" % (name, name)
                bstyle += "button[name=%s] { width: %d%% ; %s } " % (name, int(95 / (len(r) - 0.05)), style)
            bstr += '</p>'
        self.wfile.write("""<html>
    <head>
      <title>%(title)s</title>
      <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    </head>
    <body>
        <style>%(bstyle)s</style>
        <form method='post'>
        %(bstr)s
        </form>
        <script>
        $(function() {
        $("button").click(function() {
          $("button").attr("disabled", true);
          $.ajax({
            type: "POST",
            url: "/" + $(this).attr("name"),
            timeout: 3000,
            error: function(data) {
              $("button").attr("disabled", false);
            },
            success: function(data) {
              $("button").attr("disabled", false);
            }
          });
          return false;
        });
        });
        </script>
    </body>
</html>
        """ % {'title':info.title, 'bstyle':bstyle, 'bstr':bstr})

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.server.page_info.callback(self.path)

def StartHTTP(title, buttons, callback):
    actions = frozenset(itertools.chain(*buttons))
    srv = BaseHTTPServer.HTTPServer(("0.0.0.0", 3010), RequestHandler)
    srv.page_info = PageInfo(title, buttons, callback, actions)
    srv = thread.start_new_thread(srv.serve_forever, ())
    return srv
