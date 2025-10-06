# app/route.py
import os
import time
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

# Import SQLAlchemy models/session helpers
from .models import Product, create_session, get_engine

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

# Ensure engine available (models/__init__ or models.py handles DATABASE_URL)
_engine = get_engine()


# ----------------- Database helpers (SQLAlchemy) -----------------
def all_products():
    """
    Return list of products as dicts ordered by created_at desc.
    Keys: id, title, desc, photo, category, created_at (int timestamp)
    """
    sess = create_session(_engine)
    try:
        rows = sess.query(Product).order_by(Product.created_at.desc()).all()
        result = []
        for r in rows:
            result.append({
                "id": r.id,
                "title": r.title,
                "desc": r.desc,
                "photo": r.photo,
                "category": r.category,
                "created_at": int(r.created_at.timestamp()) if r.created_at else None
            })
        return result
    finally:
        sess.close()


def add_product(title, desc, photo, category):
    """
    Create a product and return the created product dict.
    """
    sess = create_session(_engine)
    try:
        p = Product(
            title=(title or "").strip(),
            desc=(desc or "").strip(),
            photo=(photo or "").strip(),
            category=category if category in CATEGORIES else (CATEGORIES[0] if CATEGORIES else "")
        )
        sess.add(p)
        sess.commit()
        sess.refresh(p)
        return {
            "id": p.id,
            "title": p.title,
            "desc": p.desc,
            "photo": p.photo,
            "category": p.category,
            "created_at": int(p.created_at.timestamp()) if p.created_at else None
        }
    finally:
        sess.close()


def update_product(pid, title, desc, photo, category):
    """
    Update an existing product. Return True if updated, False if not found.
    """
    sess = create_session(_engine)
    try:
        r = sess.query(Product).filter_by(id=pid).first()
        if not r:
            return False
        r.title = (title or "").strip()
        r.desc = (desc or "").strip()
        r.photo = (photo or "").strip()
        r.category = category if category in CATEGORIES else (CATEGORIES[0] if CATEGORIES else "")
        sess.commit()
        return True
    finally:
        sess.close()


def delete_product(pid):
    """
    Delete product by id. Return True if deleted, False if not found.
    """
    sess = create_session(_engine)
    try:
        r = sess.query(Product).filter_by(id=pid).first()
        if not r:
            return False
        sess.delete(r)
        sess.commit()
        return True
    finally:
        sess.close()


def get_product(pid):
    """
    Get a product dict by id or None.
    """
    sess = create_session(_engine)
    try:
        r = sess.query(Product).filter_by(id=pid).first()
        if not r:
            return None
        return {
            "id": r.id,
            "title": r.title,
            "desc": r.desc,
            "photo": r.photo,
            "category": r.category,
            "created_at": int(r.created_at.timestamp()) if r.created_at else None
        }
    finally:
        sess.close()


# -------- routes below (keeps your templates & behaviour) --------
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
