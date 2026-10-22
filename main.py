from orchestrator import run_single_agent, run_multi_agent_pipeline

if __name__ == "__main__":
    print("Choose which agent flow to run:")
    print("1. Single Agent Flow")
    print("2. Multi-Agent Flow")

    choice = input("Enter 1 or 2: ")
    issue_id = 42

    if choice == "1":
        run_single_agent(issue_id)
    elif choice == "2":
        run_multi_agent_pipeline(issue_id)
    else:
        print("Invalid choice.")