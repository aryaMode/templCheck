import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from fuzzywuzzy import process
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/get-schedule")
def get_schedule():
    user_input_tasks = request.args.get('tasks').split()
    # Load the dataset
    dataset = pd.read_csv('sorted_data.csv')
    print("csv Read")

    # Function to calculate average values for 'Calories (per hour)' column
    def calculate_average_calories(dataset, tasks):
        task_averages = {}
        for task in tasks:
            if task in dataset['Task'].values:
                task_calories = dataset[dataset['Task'] ==
                                        task]['Calories (per hour)'].values[0]
                task_average = sum(map(int, task_calories.split('-'))) / 2
                task_averages[task] = task_average
            else:
                matched_task, _ = process.extractOne(
                    task, dataset['Task'].values)
                task_calories = dataset[dataset['Task'] ==
                                        matched_task]['Calories (per hour)'].values[0]
                task_average = sum(map(int, task_calories.split('-'))) / 2
                task_averages[task] = task_average
        return task_averages

    # Function to sort tasks based on average calories
    def sort_tasks_by_average_calories(task_averages, user_input_tasks):
        sorted_tasks = []
        for task in user_input_tasks:
            if task in task_averages:
                sorted_tasks.append((task, task_averages[task]))
            else:
                sorted_tasks.append((task, float('-inf')))
        sorted_tasks = sorted(sorted_tasks, key=lambda x: x[1], reverse=True)
        return [task[0] for task in sorted_tasks]

    def calculate_calories_burnt(user_input_tasks, task_averages):
        calories_burnt = {}
        for task in user_input_tasks:
            if task in task_averages:
                calories_burnt[task] = task_averages[task]
        return calories_burnt

    while 'done' not in user_input_tasks:
        user_input_tasks.extend(input().split())

    # Remove the trailing 'done' from the list of tasks
    user_input_tasks.remove('done')

    # Calculate average calories for user input tasks
    task_averages = calculate_average_calories(dataset, user_input_tasks)
    calories_burnt = calculate_calories_burnt(user_input_tasks, task_averages)
    prioritized_tasks_calories_burnt = sorted(
        calories_burnt.items(), key=lambda x: x[1], reverse=True)
    return jsonify(prioritized_tasks_calories_burnt), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
