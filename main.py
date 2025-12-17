import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.simulation import run_many
from src.config import SESSION_DURATION

def get_input(prompt, default_value, value_type=str):
    user_input = input(f"{prompt} [Default: {default_value}]: ").strip()

    if not user_input:
        return default_value

    try:
        return value_type(user_input)
    except ValueError:
        print(f"Invalid input. Using default value: {default_value}")
        return default_value

def main():
    print("\n" + "=" * 40)
    print("Welcome to Surfing Monte Carlo Sim 🏄‍♀️")
    print("="*40 + "\n")
    print("Please configure the simulation parameters:\n")

    spot_level = get_input("Select Spot Level (beginner/mixed/advanced)", "beginner")
    rule_type = get_input("Select Rule Type (free-for-all/safe-distance-rule)", "free-for-all")
    num_surfer = get_input("Number of Surfaces (Enter 0 for realistic auto-count)", 0, int)
    if num_surfer == 0:
        num_surfer = None
    duration = get_input("Simulation Duration (seconds)", SESSION_DURATION, int)
    iterations = get_input("Number of Iterations", 30, int)

    print("\n" + "-" * 40)
    print("Starting Simulation")
    print("-" * 40 + "\n")

    try:
        stats = run_many(
            number_of_runs=iterations,
            spot_level=spot_level,
            rule_type=rule_type,
            num_surfer=num_surfer,
            duration=duration,
            mode="realistic")[1]

        print("\n Simulation Results:")
        print(f"  - Spot Level: {spot_level}")
        print(f"  - Surfers (Approx): {round(stats['n_surfers'])}")
        print(f"  - Success Rides: {stats['avg_success_count']:.2f} rides/surfer")
        print(f"  - Collisions: {stats['avg_collision_count']:.2f} collisions/surfer")
        print(f"  - Fairness (Gini): {stats['fairness']:.4f} (Gini Index)")
        print(f"  - Avg Wait Time: {stats['avg_waiting_time']:.1f} sec")

    except Exception as e:
        print(f"\n Error: {e}")
    print("\nDone.")

if __name__ == '__main__':
    main()



