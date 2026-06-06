"""
apps_gform.py — Generic CRUD form + full table handler.
Serves any class via /gform/<cname>.
"""
from flask import request, render_template, session
import sys, os, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'classes'))

DATE_FIELDS = {'created_date', 'redemption_date'}

def _get_registry():
    from airline    import Airline
    from promotion  import Promotion
    from reward     import Reward
    from redemption import Redemption
    return {
        'Airline':    Airline,
        'Promotion':  Promotion,
        'Reward':     Reward,
        'Redemption': Redemption,
    }

FK_SOURCES = {
    'reward_id':    ('Reward',    'reward_id',    'name'),
    'promotion_id': ('Promotion', 'promotion_id', 'name'),
}

_prev_options = {}

def _parse_date(value):
    try:
        datetime.datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        raise ValueError(f"Data inválida '{value}'. Use o formato YYYY-MM-DD (ex: 2024-01-15).")

def apps_gform(cname):
    global _prev_options

    registry = _get_registry()
    cls = registry.get(cname)
    if cls is None:
        return f"<h2>Unknown class: {cname}</h2>", 404

    prev_option = _prev_options.get(cname, "")
    butshow  = "enabled"
    butedit  = "disabled"
    form_error = ""
    option   = request.args.get("option", "")

    if option == "edit":
        butshow, butedit = "disabled", "enabled"

    elif option == "delete":
        obj = cls.current()
        if obj:
            cls.remove(obj.id)
            obj = cls.previous()
            if obj is None:
                obj = cls.first()

    elif option == "insert":
        butshow, butedit = "disabled", "enabled"

    elif option == "cancel":
        pass

    elif prev_option == "insert" and option == "save":
        try:
            for att in cls.att[1:]:
                if att in DATE_FIELDS:
                    _parse_date(request.form.get(att, ""))
            strobj = str(cls.get_id(0))
            for att in cls.att[1:]:
                strobj += ";" + str(request.form.get(att, ""))
            obj = cls.from_string(strobj)
            cls.insert(obj.id)
            cls.last()
        except ValueError as e:
            form_error = str(e)
            butedit = "enabled"
            butshow = "disabled"
            prev_option = "insert"

    elif prev_option == "edit" and option == "save":
        obj = cls.current()
        if obj:
            try:
                for att in cls.att[1:]:
                    if att in DATE_FIELDS:
                        _parse_date(request.form.get(att, ""))
                for att in cls.att[1:]:
                    val = request.form.get(att, "")
                    current_val = getattr(obj, att)
                    if isinstance(current_val, int):
                        val = int(val) if val else 0
                    setattr(obj, att, val)
                cls.update(obj.id)
            except ValueError as e:
                form_error = str(e)
                butedit = "enabled"
                butshow = "disabled"

    elif option == "first":    cls.first()
    elif option == "previous": cls.previous()
    elif option == "next":     cls.nextrec()
    elif option == "last":     cls.last()
    elif option == "exit":
        from airline import Airline
        from promotion import Promotion
        from reward import Reward
        from redemption import Redemption
        return render_template("home.html",
                               ulogin=session.get("user"),
                               n_airlines=len(Airline.lst),
                               n_promotions=len(Promotion.lst),
                               n_rewards=len(Reward.lst),
                               n_redemptions=len(Redemption.lst))

    if not form_error:
        _prev_options[cname] = option

    obj = cls.current()

    fields = {}
    pk = cls.att[0]
    if option == "insert" or len(cls.lst) == 0:
        fields[pk] = cls.get_id(0)
        for att in cls.att[1:]:
            fields[att] = ""
    else:
        for att in cls.att:
            fields[att] = getattr(obj, att) if obj else ""

    fk_options = {}
    for att in cls.att:
        if att in FK_SOURCES:
            src_name, src_id_att, src_label_att = FK_SOURCES[att]
            src_cls = registry.get(src_name)
            if src_cls:
                fk_options[att] = [
                    (getattr(o, src_id_att), getattr(o, src_label_att))
                    for o in src_cls.obj.values()
                ]

    all_records = [
        {att: getattr(o, att) for att in cls.att}
        for o in cls.obj.values()
    ]

    return render_template("gform.html",
                           cname=cname,
                           att=cls.att,
                           fields=fields,
                           fk_options=fk_options,
                           butshow=butshow,
                           butedit=butedit,
                           form_error=form_error,
                           all_records=all_records,
                           ulogin=session.get("user"))
