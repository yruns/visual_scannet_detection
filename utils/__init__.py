from .agent import Agent
from .comm import TempFile
from loguru import logger

logger.add("logs/{time}.log")

agent = Agent()
