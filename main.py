from gmm.main import create_app
import os
print (os.getcwd())
app = create_app(os.getenv('BOILERPLATE_ENV') or 'dev')
#app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)
app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)

