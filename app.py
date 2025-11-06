from flask import Flask, render_template, request
import networkx as nx

app = Flask(__name__)

def parse_courses(form):
    courses = []
    course_names = form.getlist("course")
    professors = form.getlist("professor")
    students_lists = form.getlist("students")
    for cname, prof, students in zip(course_names, professors, students_lists):
        course = {
            "id": cname.strip(),
            "professor": prof.strip(),
            "students": [s.strip() for s in students.split(",") if s.strip()]
        }
        courses.append(course)
    return courses

def build_conflict_graph(courses):
    G = nx.Graph()
    for course in courses:
        G.add_node(course["id"])
    for i in range(len(courses)):
        for j in range(i + 1, len(courses)):
            shared_prof = courses[i]["professor"] == courses[j]["professor"]
            shared_stud = bool(set(courses[i]["students"]) & set(courses[j]["students"]))
            if shared_prof or shared_stud:
                G.add_edge(courses[i]["id"], courses[j]["id"])
    return G

def greedy_coloring(G):
    coloring = {}
    for node in sorted(G.nodes(), key=lambda x: G.degree[x], reverse=True):
        neighbor_colors = {coloring[n] for n in G.neighbors(node) if n in coloring}
        color = 1
        while color in neighbor_colors:
            color += 1
        coloring[node] = color
    return coloring

@app.route("/", methods=["GET", "POST"])
def home():
    schedule = None
    courses = []
    input_rows = 8
    if request.method == "POST":
        courses = parse_courses(request.form)
        G = build_conflict_graph(courses)
        coloring = greedy_coloring(G)
        schedule = {course_id: f"Time Slot {color}" for course_id, color in coloring.items()}
        input_rows = len(courses) + 1
    return render_template("index.html", courses=courses, schedule=schedule, input_rows=input_rows)

if __name__ == "__main__":
    app.run(debug=True)
