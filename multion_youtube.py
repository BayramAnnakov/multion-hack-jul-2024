import dotenv

dotenv.load_dotenv()

import os

from multion.client import MultiOn

client = MultiOn(
    api_key=os.getenv("MULTION_API_KEY")
)

