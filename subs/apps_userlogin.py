from flask import request, render_template, session
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'classes'))
from userlogin import Userlogin

prev_option = ""

def apps_userlogin():
    global prev_option

    ulogin = session.get("user")
    group  = ""
    if ulogin:
        uid = Userlogin.get_user_id(ulogin)
        if uid != 0:
            group = Userlogin.obj[uid]._usergroup

    butshow = "enabled"
    butedit = "disabled"
    msg     = ""
    option  = request.args.get("option", "")

    if option == "edit":
        butshow, butedit = "disabled", "enabled"

    elif option == "delete" and group == "admin":
        obj = Userlogin.current()
        if obj:
            Userlogin.remove(obj.id)
            obj = Userlogin.previous()
            if obj is None:
                obj = Userlogin.first()

    elif option == "insert" and group == "admin":
        butshow, butedit = "disabled", "enabled"

    elif option == "cancel":
        pass

    elif prev_option == "insert" and option == "save" and group == "admin":
        encrypted = Userlogin.set_password(request.form["password"])
        strobj  = str(Userlogin.get_id(0))
        strobj += ";" + request.form["user"]
        strobj += ";" + request.form["usergroup"]
        strobj += ";" + encrypted
        obj = Userlogin.from_string(strobj)
        Userlogin.insert(obj.id)
        Userlogin.last()
        msg = "User created."

    elif prev_option == "edit" and option == "save":
        obj = Userlogin.current()
        if obj:
            raw = request.form.get("password", "")
            if raw:
                obj._password = Userlogin.set_password(raw)
            if group == "admin":
                obj._usergroup = request.form.get("usergroup", obj._usergroup)
            Userlogin.update(obj.id)
            msg = "Saved."

    elif option == "first"    and group == "admin": Userlogin.first()
    elif option == "previous" and group == "admin": Userlogin.previous()
    elif option == "next"     and group == "admin": Userlogin.nextrec()
    elif option == "last"     and group == "admin": Userlogin.last()
    elif option == "exit":
        from airline import Airline
        from promotion import Promotion
        from reward import Reward
        from redemption import Redemption
        return render_template("home.html",
                               ulogin=ulogin,
                               n_airlines=len(Airline.lst),
                               n_promotions=len(Promotion.lst),
                               n_rewards=len(Reward.lst),
                               n_redemptions=len(Redemption.lst))

    prev_option = option
    obj = Userlogin.current()

    cur_uid       = obj.id         if obj and option != "insert" else Userlogin.get_id(0)
    cur_user      = obj._user      if obj and option != "insert" else ""
    cur_usergroup = obj._usergroup if obj and option != "insert" else ""

    # Build users list for table (admin only)
    all_users = [
        {"uid": o.id, "user": o._user, "usergroup": o._usergroup}
        for o in Userlogin.obj.values()
    ]

    return render_template("userlogin.html",
                           butshow=butshow, butedit=butedit,
                           group=group,
                           uid=cur_uid,
                           user=cur_user,
                           usergroup=cur_usergroup,
                           ulogin=ulogin,
                           msg=msg,
                           all_users=all_users)
