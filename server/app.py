from openenv.core.env_server.http_server import create_app
from .environment import RegisterAction, RegisterObservation, RegisterEnvironment
app = create_app(RegisterEnvironment, RegisterAction, RegisterObservation,
                 env_name='register_lab', max_concurrent_envs=8)
