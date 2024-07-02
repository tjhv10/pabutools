from flask import Flask, render_template, request
from myapp.cstv import *
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        projects = request.form.getlist('projects')
        costs = request.form.getlist('costs')
        donations_data = request.form.getlist('donations')

        # Convert inputs to appropriate structures
        projects_list = Instance([Project(projects[i], int(costs[i])) for i in range(len(projects))])
        
        # Processing donors input
        donors_list = []
        for donor_data in donations_data:
            donor_donations = map(str, donor_data.split(','))
            donation_dict = {projects[i]: int(donation) for i, donation in enumerate(donor_donations)}
            donors_list.append(CumulativeBallot(donation_dict))
        donors_profile = Profile(donors_list)
        # Call the CSTV algorithm
        selected_projects = cstv_budgeting_combination(projects_list, donors_profile,"ewt")

        return render_template('result.html', selected_projects=selected_projects)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
