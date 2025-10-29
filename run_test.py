from blog import create_app
from blog.settings import TestConfig

app = create_app(TestConfig)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
