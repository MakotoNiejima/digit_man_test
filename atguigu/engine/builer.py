from pathlib import Path

from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.task.flow.loader import FlowLoader

PROJECT_ROOT_DIR = Path(__file__).resolve().parents[2]
FLOW_CONFIG_DIR = PROJECT_ROOT_DIR / "flow-config"
FLOW_CONFIG_FILE = ["system_flows.yml", "user_flows.yml"]

def build_dialogue_engine():
	flow_list = FlowLoader().load_many_yaml([FLOW_CONFIG_DIR / file for file in FLOW_CONFIG_FILE])
	return DialogueEngine(

	)