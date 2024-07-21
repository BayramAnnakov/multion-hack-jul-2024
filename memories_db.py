import dotenv

dotenv.load_dotenv()

from mem0 import Memory

m = Memory()

memories = m.search(query="Bill Ackman", user_id="Bayram")

print(memories)

memories_all = m.get_all()

print(memories_all)
