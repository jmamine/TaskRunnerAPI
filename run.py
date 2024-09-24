import os

from dotenv import load_dotenv

from app import app, scheduler
from app.routes import task_blueprint
from config import get_config

load_dotenv()

app.register_blueprint(task_blueprint, url_prefix='/task')
env = os.environ.get('FLASK_ENV')
config = get_config(env)
app.config.from_object(config)



if __name__ == "__main__":
    scheduler.start()
    
    app.run(host='0.0.0.0', port=config.PORT, debug=config.DEBUG)