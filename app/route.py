import os, json, time
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

main = Blueprint("main", __name__, template_folder="templates")

# -------- Business profile (same as before) --------
PROFILE = {
    "brand": "GameX PC Hub",
    "tagline": "Custom Gaming PC • Laptops • Accessories",
    "owner_title": "Owner",
    "phone_display": "8653568180",
    "phone_raw": "+918653568180",
    "email": "saidmessi4321@gmail.com",
    "maps_link": "https://maps.app.goo.gl/SeWHTkt9shZ4iVzf6",
    "instagram": "https://www.instagram.com/gamexpchub?igsh=MWFkdHo4ajRlc214aQ==",
    "facebook": "https://www.facebook.com/share/1FRQbyFfHE/",
    "youtube": "https://youtube.com/@gamexpchub",
    "map_review": "https://maps.app.goo.gl/UdeBHbvDXAYmRU2D7",
    "wa_group": "https://chat.whatsapp.com/F7Hnm86n2Cx3TjAiMlXs9I?mode=ems_copy_t",
    "address": "Your Street, Your City, Your State, India",
    "avatar": "https://i.postimg.cc/Dzyh5yRb/IMG-20251005-034327.jpg",
    "logo": "https://i.postimg.cc/gJFwnhxr/IMG-20251005-034017.png",
}

CATEGORIES = ["Second Hand", "Computer", "Printer", "Tabs", "Accessories"]
ADMIN_PIN = "8180"

DATA_PATH = os.path.join(os.path.dirname(__file__), "data.json")

def _default():
    return {"products": [], "seq": 1}

def _repair_and_return_default():
    """If file invalid/empty, rewrite a clean default JSON and return it."""
    payload = _default()
    try:
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception:
        # read-only FS fallback: do nothing, just return default in-memory
        pass
    return payload

def _load():
    """Safe load: if missing/empty/invalid -> auto repair & return default."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            if not txt:
                return _repair_and_return_default()
            return json.loads(txt)
    except Exception:
        return _repair_and_return_default()

def _save(payload):
    """Safe save with atomic temp write, then replace."""
    tmp = DATA_PATH + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp, DATA_PATH)
    except Exception:
        # last resort: try direct write
        try:
            with open(DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception:
            # read-only FS: ignore (in-memory only)
            pass

def all_products():
    return _load().get("products", [])

def next_id():
    data = _load()
    nid = int(data.get("seq", 1))
    data["seq"] = nid + 1
    _save(data)
    return nid

def add_product(title, desc, photo, category):
    p = {
        "id": next_id(),
        "title": (title or "").strip(),
        "desc": (desc or "").strip(),
        "photo": (photo or "").strip(),
        "category": category if category in CATEGORIES else CATEGORIES[0],
        "created_at": int(time.time()),
    }
    data = _load()
    data.setdefault("products", []).insert(0, p)
    _save(data)
    return p

def update_product(pid, title, desc, photo, category):
    data = _load()
    for p in data.get("products", []):
        if p["id"] == pid:
            p["title"] = (title or "").strip()
            p["desc"] = (desc or "").strip()
            p["photo"] = (photo or "").strip()
            p["category"] = category if category in CATEGORIES else CATEGORIES[0]
            _save(data)
            return True
    return False

def delete_product(pid):
    data = _load()
    before = len(data.get("products", []))
    data["products"] = [p for p in data.get("products", []) if p["id"] != pid]
    _save(data)
    return len(data["products"]) < before

def get_product(pid):
    for p in all_products():
        if p["id"] == pid:
            return p
    return None

# -------- routes below (unchanged from my last message) --------
@main.route("/")
def profile():
    products = all_products()[:9]
    return render_template("profile.html", p=PROFILE, products=products,
                           categories=CATEGORIES, admin=session.get("admin", False))

@main.route("/products")
def products():
    cat = request.args.get("category", "").strip()
    edit_id = request.args.get("edit", type=int)
    selected = cat if cat in CATEGORIES else None

    items = all_products()
    if selected:
        items = [x for x in items if x["category"] == selected]

    edit_item = get_product(edit_id) if edit_id else None

    return render_template("products.html", p=PROFILE, products=items, categories=CATEGORIES,
                           selected=selected, edit_item=edit_item, admin=session.get("admin", False))

@main.route("/login", methods=["POST"])
def login():
    pin = (request.form.get("pin") or "").strip()
    if pin == ADMIN_PIN:
        session["admin"] = True
        flash("✅ Admin logged in", "success")
    else:
        flash("❌ Wrong PIN", "error")
    return redirect(request.referrer or url_for("main.profile"))

@main.route("/logout")
def logout():
    session.pop("admin", None)
    flash("ℹ️ Logged out", "info")
    return redirect(request.referrer or url_for("main.profile"))

@main.route("/add_product", methods=["POST"])
def add_product_route():
    if not session.get("admin"):
        flash("Not authorized ❌", "error")
        return redirect(url_for("main.profile"))
    title = request.form.get("title", "")
    desc = request.form.get("desc", "")
    photo = request.form.get("photo", "")
    category = request.form.get("category", CATEGORIES[0])
    if not title.strip():
        flash("Title is required", "error")
        return redirect(request.referrer or url_for("main.profile"))
    add_product(title, desc, photo, category)
    flash("✅ Product added", "success")
    return redirect(request.referrer or url_for("main.profile"))

@main.route("/edit_product/<int:pid>", methods=["POST"])
def edit_product_route(pid):
    if not session.get("admin"):
        flash("Not authorized ❌", "error")
        return redirect(url_for("main.products"))
    title = request.form.get("title", "")
    desc = request.form.get("desc", "")
    photo = request.form.get("photo", "")
    category = request.form.get("category", CATEGORIES[0])
    if not title.strip():
        flash("Title is required", "error")
        return redirect(url_for("main.products", edit=pid))
    ok = update_product(pid, title, desc, photo, category)
    flash("✅ Product updated" if ok else "❌ Product not found", "success" if ok else "error")
    return redirect(url_for("main.products"))

@main.route("/delete_product/<int:pid>", methods=["POST"])
def delete_product_route(pid):
    if not session.get("admin"):
        flash("Not authorized ❌", "error")
        return redirect(url_for("main.products"))
    ok = delete_product(pid)
    flash("🗑️ Product deleted" if ok else "❌ Product not found", "success" if ok else "error")
    return redirect(request.referrer or url_for("main.products"))
