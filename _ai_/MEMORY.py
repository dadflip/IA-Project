import json
import os
from collections import defaultdict
import threading

class MemoryManager:
    def __init__(self, file_path="memory.json"):
        self.file_path = file_path
        self.memory = self.load_memory()
        self.index = self.create_index()
        self.lock = threading.Lock()  # Lock for thread-safe operations

    def load_memory(self):
        # Check if the file exists
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                # If decoding error occurs, attempt repair
                print("Corrupted JSON file. Attempting repair...")
                self.repair_json()
                with open(self.file_path, "r") as file:
                    return json.load(file)
        # Return an empty dictionary if the file does not exist or is corrupted
        return {}

    def save_memory(self):
        with self.lock:
            try:
                with open(self.file_path, "w") as file:
                    json.dump(self.memory, file, indent=4)
            except Exception as e:
                print(f"Error while saving memory: {e}")

    def add_entry(self, state, action, reward, next_state):
        entry = {
            "state": state,
            "action": action,
            "reward": reward,
            "next_state": next_state
        }
        state_key = str(state)  # Convert state to string as JSON keys must be strings
        with self.lock:
            if state_key not in self.memory:
                self.memory[state_key] = []
            self.memory[state_key].append(entry)
            self.update_index(state_key, entry)
        self.save_memory()

    def create_index(self):
        """
        Create an index for quick lookup of state-action pairs.
        """
        index = defaultdict(list)
        for state_key, entries in self.memory.items():
            for entry in entries:
                action = tuple(entry["action"])
                index[(state_key, action)].append(entry)
        return index

    def update_index(self, state_key, entry):
        """
        Update the index with a new entry.
        """
        action = tuple(entry["action"])
        self.index[(state_key, action)].append(entry)

    def get_entries(self, state, action):
        """
        Get entries from the memory for a given state and action.
        """
        state_key = str(state)
        action_tuple = tuple(action)
        with self.lock:
            return self.index.get((state_key, action_tuple), [])

    def repair_json(self):
        """
        Repairs the JSON file in case of incomplete structure or missing characters.
        """
        try:
            with open(self.file_path, "r") as file:
                corrupted_content = file.read()
            
            # Automatically add missing braces or brackets
            repaired_content = corrupted_content
            if corrupted_content.count("{") > corrupted_content.count("}"):
                repaired_content += "}" * (corrupted_content.count("{") - corrupted_content.count("}"))
            elif corrupted_content.count("[") > corrupted_content.count("]"):
                repaired_content += "]" * (corrupted_content.count("[") - corrupted_content.count("]"))

            # Final check with `json.loads`
            try:
                json.loads(repaired_content)
            except json.JSONDecodeError:
                # Remove invalid data if repair fails
                print("Unable to fully repair the JSON file. Resetting...")
                repaired_content = "{}"

            with open(self.file_path, "w") as file:
                file.write(repaired_content)

        except Exception as e:
            print(f"Failed to repair JSON file: {e}")
            # Reset the file if irreparable
            with open(self.file_path, "w") as file:
                file.write("{}")
