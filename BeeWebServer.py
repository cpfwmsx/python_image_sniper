import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from sakshat import SAKSHAT
import time
import commands

define("port", default=8000, help="run on the given port", type=int)
SAKS = SAKSHAT()


class BeeWebServer(tornado.web.RequestHandler):
    def get(self):
        page = self.get_argument('page', '0')
        err_page = page
        self.write("exception in page: " + page)
        b = SAKS.buzzer
        # 哔1秒
        b.beep(1)
        show_num = str(page)
        SAKS.digital_display.show(show_num)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/bee", BeeWebServer)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
