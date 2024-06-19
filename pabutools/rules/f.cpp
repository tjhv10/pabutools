#include <iostream>
#include <vector>
#include <unordered_map>
#include <algorithm>

// Define Project class
class Project {
public:
    std::string name;
    double cost;
    
    Project(std::string n, double c) : name(n), cost(c) {}
};

// Define CumulativeBallot class (assuming it as a struct)
class CumulativeBallot {
public:
    std::unordered_map<std::string, double> donations;
    
};

// Define Instance class (assuming it as a struct)
struct Instance {
    std::vector<Project> projects;
    
    void add(Project p) {
        projects.push_back(p);
    }
    
    void remove(Project p) {
        projects.erase(std::remove_if(projects.begin(), projects.end(),
                                      [&](const Project& pr) { return pr.name == p.name; }),
                       projects.end());
    }
    
    void clear() {
        projects.clear();
    }
    
    bool empty() const {
        return projects.empty();
    }
    
    void pop() {
        if (!projects.empty()) {
            projects.pop_back();
        }
    }
};

// Define logger class with a debug method
class Logger {
public:
    void debug(std::string msg) {
        std::cout << "DEBUG: " << msg << std::endl;
    }
};

// Function to distribute support of an eliminated project to remaining projects
// Function to distribute support of an eliminated project to remaining projects
Instance distribute_project_support(Instance projects, Project eliminated_project, std::vector<CumulativeBallot>& donors, Logger& logger) {
    std::string eliminated_name = eliminated_project.name;
    logger.debug("Distributing support of eliminated project: " + eliminated_name);
    
    for (auto& donor : donors) {
        auto it = donor.donations.find(eliminated_name);
        if (it == donor.donations.end()) {
            continue;  // Handle case where project doesn't exist in donor's donations
        }
        
        double toDistribute = it->second;
        double total = 0.0;
        for (const auto& pair : donor.donations) {
            total += pair.second;
        }
        
        if (total == 0.0) {
            continue;
        }
        
        for (auto& pair : donor.donations) {
            if (pair.first != eliminated_name) {
                double part = pair.second / total;
                pair.second += toDistribute * part;
                donor.donations[eliminated_name] = 0.0;
            }
        }
    }
    
    return projects;
}


// Main function for elimination with transfers
bool elimination_with_transfers(std::vector<CumulativeBallot>& donors, Instance& projects, Instance& eliminated_projects, Logger& logger) {
    if (projects.empty() || projects.projects.size() < 2) {
        logger.debug("Not enough projects to eliminate.");
        if (!projects.empty()) {
            eliminated_projects.add(projects.projects.back());
            projects.pop();
        }
        return false;
    }
    
    auto min_project = std::min_element(projects.projects.begin(), projects.projects.end(),
                                        [&](const Project& p1, const Project& p2) {
                                            double sum_p1 = 0.0, sum_p2 = 0.0;
                                            for (auto& donor : donors) {
                                                sum_p1 += donor.donations[p1.name];
                                                sum_p2 += donor.donations[p2.name];
                                            }
                                            return (sum_p1 - p1.cost) < (sum_p2 - p2.cost);
                                        });
    
    logger.debug("Eliminating project with least excess support: " + min_project->name);
    projects = distribute_project_support(projects, *min_project, donors, logger);
    // projects.remove(*min_project);
    // eliminated_projects.add(*min_project);
    
    return true;
}

// Example usage
int main() {
    Logger logger;
    
    // Example projects and donors
    Project project_A("Project A", 30);
    Project project_B("Project B", 30);
    Project project_C("Project C", 20);
    
    CumulativeBallot donor1 = CumulativeBallot();
    donor1.donations = {{"Project A", 10.0}, {"Project B", 0.0}, {"Project C", 5.0}};
    CumulativeBallot donor2 = CumulativeBallot();
    donor2.donations = {{"Project A", 10.0}, {"Project B", 0.0}, {"Project C", 5.0}};
    
    std::vector<CumulativeBallot> donors{donor1, donor2};
    Instance projects;
    projects.add(project_A);
    projects.add(project_B);
    projects.add(project_C);
    Instance eliminated_projects;
    
    elimination_with_transfers(donors, projects, eliminated_projects, logger);
    
    // Output updated donations for donors
    std::cout << "Donor 1:" << std::endl;
    std:: cout<<"hi"<<std::endl;
    for (const auto& pair : donor1.donations) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }
    
    std::cout << "Donor 2:" << std::endl;
    for (const auto& pair : donor2.donations) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }
    return 0;
}
