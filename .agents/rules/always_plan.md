# Always Plan and Approve First

## Behavioral Constraints
* **Propose Plans First**: Before making any code modifications or running commands that change codebase state, the agent MUST write or update the implementation plan (`implementation_plan.md`) and request feedback.
* **Await Explicit Approval**: The agent MUST STOP and wait for the user's explicit approval (chat input or clicking "Proceed") before editing or rewriting any file in the workspace.
* **Explain Mathematical & Design Concepts First**: When requested to adjust visual, math, or design settings (e.g. histogram bining on the X-axis), the agent MUST explain the underlying concept or options in the chat and wait for user direction before preparing the plan.
