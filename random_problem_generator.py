from config import BOARD_SIZE
import random
import json

def generate_random_board(size):
    num_pairs = (size * size) // 2
    entities = list(range(num_pairs)) * 2
    random.shuffle(entities)
    board = [entities[i * size:(i + 1) * size] for i in range(size)]
    return board

def create_random_problem_json(output_file="problem.json", min_size=4, max_size=24):
    size_options = [s for s in range(min_size, max_size+1) if s % 2 == 0]
    # size = random.choice(size_options)
    size = BOARD_SIZE
    board = generate_random_board(size)
    problem_data = {
        "startsAt": 0,
        "problem": {
            "field": {
                "size": size,
                "entities": board
            }
        }
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(problem_data, f, ensure_ascii=False, indent=2)
    print(f"Random problem generated with size {size} and written to {output_file}")