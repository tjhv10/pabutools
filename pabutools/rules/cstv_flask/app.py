from flask import Flask, flash, render_template, request
from cstv import *

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        projects = request.form.getlist('projects')
        costs = request.form.getlist('costs')
        donors_data = request.form.getlist('donors')
        donations_data = request.form.getlist('donations')

        # Convert inputs to appropriate structures
        projects_list = Instance([Project(projects[i], int(costs[i])) for i in range(len(projects))])
        
        # Processing donors input
        donors_list = []
        total_sum = 0
        flag = True
        for donor_data in donations_data:
            donor_donations = list(map(int, donor_data.split(',')))
            donation_dict = {projects[i]: donor_donations[i] for i in range(len(donor_donations))}
            if flag:
                total_sum = sum(donation_dict.values())
                flag = False
            else:
                if total_sum != sum(donation_dict.values()):
                    flash("Warning: The total donation for a donor does not match the expected amount.")
            donors_list.append(CumulativeBallot(donation_dict))

        donors_profile = Profile(donors_list)
        # Call the CSTV algorithm
        selected_projects = cstv_budgeting_combination(projects_list, donors_profile, "ewt")

        return render_template('result.html', selected_projects=selected_projects)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
