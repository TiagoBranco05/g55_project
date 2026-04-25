from flask import Flask, render_template, request, session
from classes.person import Person
from datafile import filename

app = Flask(__name__)

Person.read(filename + 'Person.db')
prev_option = ""
app.secret_key = 'BAD_SECRET_KEY'

@app.route("/", methods=["post","get"])
def index():
    global prev_option
    butshow, butedit = "enabled", "disabled"
    option = request.args.get("option")
    if option == "edit":
        butshow, butedit = "disabled", "enabled"
    elif option == "delete":
        obj = Person.current()
        Person.remove(obj.id)
        if not Person.previous():
            Person.first()
    elif option == "insert":
        butshow, butedit = "disabled", "enabled"
    elif option == 'cancel':
        pass
    elif prev_option == 'insert' and option == 'save':
        strobj = str(Person.get_id(0))
        strobj = strobj + ';' + request.form["name"] + ';' + \
        request.form["dob"] + ';' + request.form["salary"]
        obj = Person.from_string(strobj)
        Person.insert(obj.id)
        Person.last()
    elif prev_option == 'edit' and option == 'save':
        obj = Person.current()
        obj.name = request.form["name"]
        obj.dob = request.form["dob"]
        obj.salary = float(request.form["salary"])
        Person.update(obj.id)
    elif option == "first":
        Person.first()
    elif option == "previous":
        Person.previous()
    elif option == "next":
        Person.nextrec()
    elif option == "last":
        Person.last()
    elif option == 'exit':
        return "<h1>Thank you for using this app</h1>"
    prev_option = option
    obj = Person.current()
    if option == 'insert' or len(Person.lst) == 0:
        id = 0
        id = Person.get_id(id)
        name = dob = salary = ""
    else:
        id = obj.id
        name = obj.name
        dob = obj.dob
        salary = obj.salary
    return render_template("index.html", butshow=butshow, butedit=butedit, 
                    id=id,name = name,dob=dob,salary=salary, 
                    ulogin=session.get("user"))
        
if __name__ == '__main__':
    app.run()