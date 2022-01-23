from gmm.main import create_app
import os
print (os.getcwd())
app = create_app(os.getenv('BOILERPLATE_ENV') or 'dev')
app.run(host="localhost", port=5000, debug=True, use_reloader=False)