from workflow import build_workflow

if __name__ == "__main__":
    print("Email Assistant running. Waiting for new mail...")
    app = build_workflow()
    # Invokes once and blocks in the listener until an email arrives
    app.invoke({})
    print("Workflow completed.")