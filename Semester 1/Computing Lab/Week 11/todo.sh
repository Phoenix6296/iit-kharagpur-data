#!/bin/bash

TODO_FILE="todo_list.txt"

add_task() {
    local description="$1"
    local priority="$2"

    if [[ "$priority" != "high" && "$priority" != "medium" && "$priority" != "low" ]]; then
        echo "Error: Invalid priority level. Use 'high', 'medium', or 'low'."
        exit 1
    fi

    if [[ ! -f "$TODO_FILE" ]]; then
        task_id=1
    else
        task_id=$(($(tail -n 1 "$TODO_FILE" | cut -d'|' -f1) + 1))
    fi

    echo "$task_id | $description | $priority | incomplete" >> "$TODO_FILE"
    echo "Task added successfully: $description with priority $priority."
}

show_tasks() {
    if [[ ! -f "$TODO_FILE" ]]; then
        echo "No tasks found."
        exit 0
    fi
    awk -F'|' '{
        if ($4 ~ /incomplete/) {
            if ($3 ~ /high/) priority = 1;
            else if ($3 ~ /medium/) priority = 2;
            else if ($3 ~ /low/) priority = 3;
            printf "%d|%s\n", priority, $0;
        } else {
            if ($3 ~ /high/) priority = 4; # Completed high after incomplete
            else if ($3 ~ /medium/) priority = 5; # Completed medium
            else if ($3 ~ /low/) priority = 6; # Completed low
            printf "%d|%s\n", priority, $0;
        }
    }' "$TODO_FILE" | sort -n | cut -d'|' -f2- | column -t -s "|"
}

complete_task() {
    local task_id="$1"

    if [[ ! -f "$TODO_FILE" ]]; then
        echo "Error: No tasks found."
        exit 1
    fi

    if ! grep -q "^$task_id |" "$TODO_FILE"; then
        echo "Error: Task ID $task_id not found."
        exit 1
    fi

    sed -i "" -e "/^$task_id |/ s/incomplete/complete/" "$TODO_FILE"
    echo "Task $task_id marked as complete."
}

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <operation> [arguments]"
    exit 1
fi

operation="$1"

case "$operation" in
    add)
        if [[ $# -ne 3 ]]; then
            echo "Error: Incorrect number of arguments for add."
            echo "Usage: $0 add <task_description> <priority>"
            exit 1
        fi
        add_task "$2" "$3"
        ;;
    show)
        if [[ $# -ne 1 ]]; then
            echo "Error: Incorrect number of arguments for show."
            echo "Usage: $0 show"
            exit 1
        fi
        show_tasks
        ;;
    complete)
        if [[ $# -ne 2 ]]; then
            echo "Error: Incorrect number of arguments for complete."
            echo "Usage: $0 complete <task_id>"
            exit 1
        fi
        complete_task "$2"
        ;;
    *)
        echo "Error: Invalid operation. Use 'add', 'show', or 'complete'."
        exit 1
        ;;
esac
