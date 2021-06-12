# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import jsonify, render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from app import db, login_manager
from app.base import blueprint
from app.base.forms import LoginForm, CreateAccountForm
from app.base.models import User, Post, Category

from app.base.util import verify_pass

@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))

## Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        
        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()
        
        # Check the password
        if user and verify_pass( password, user.password):

            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template( 'accounts/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template( 'accounts/login.html',
                                form=login_form)
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username  = request.form['username']
        email     = request.form['email'   ]

        # Check usename exists
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Username already registered',
                                    success=False,
                                    form=create_account_form)

        # Check email exists
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Email already registered', 
                                    success=False,
                                    form=create_account_form)

        # else we can create the user
        user = User(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template( 'accounts/register.html', 
                                msg='User created please <a href="/login">login</a>', 
                                success=True,
                                form=create_account_form)

    else:
        return render_template( 'accounts/register.html', form=create_account_form)

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))


# 文章
@blueprint.route('/posts-edit', methods=["POST", "GET"])
def posts():
    if not current_user.is_authenticated:
        return 'Forbidden', 403
    results = db.session.query(Post, Category).filter(Post.category_id == Category.id).order_by(Post.id.desc()).all()
    categories = Category.query.all()
    return render_template('posts/posts-edit.html', 
                            results = results, 
                            categories = categories,
                            segment='posts-edit')


@blueprint.route('/delete-posts',  methods=["POST", "GET"])
def delete_type():
    if not current_user.is_authenticated:
        return 'Forbidden', 403
    post_id = request.form.get('id')
    query = Post.query.filter_by(id = post_id).first()
    db.session.delete(query)
    db.session.commit()
    return '', 200  

@blueprint.route('/update-posts', methods=["POST", "GET"])
def update_posts():
    if not current_user.is_authenticated:
        return 'Forbidden', 403
    post_id = request.form.get('id')
    result = Post.query.filter_by(id = post_id).first()
    return jsonify({
                    "id": f"{result.id}",
                    'title': f"{result.title}",
                    'content': f"{result.content}",
                    'category_id': f"{result.category_id}",
                    'image': f"{result.image}",
                    'published': f"{result.published}",
                    "views": f"{result.views}",
                    "slug": f"{result.slug}"
                  })


@blueprint.route('/update-posts-action', methods=["POST", "GET"])
def update_posts_action():
    if not current_user.is_authenticated:
        return 'Forbidden', 403    
    post_id = request.form.get('id')
    title = request.form.get('title')
    category_id = request.form.get('category_id')
    image = request.form.get('image')
    content = request.form.get('content')
    published = request.form.get('published')
    views = request.form.get('views')
    slug = request.form.get('slug')

    if post_id == '':
        # 新增資料
        q = Post(category_id = category_id,
                 title = title,
                 content = content,
                 image = image,
                 published = published,
                 views = views,
                 slug=slug
                )
        db.session.add(q)             
        db.session.commit()
        
    else:
        # 更新資料    
        q = Post.query.filter_by(id = post_id).first()
        q.category_id = category_id
        q.title = title
        q.content = content
        q.published = published
        q.views = views
        q.image = image
        q.slug = slug
        db.session.commit()
    
    return redirect('/posts-edit')

# 分類
@blueprint.route('/category-edit', methods=["POST", "GET"])
def category():
    if not current_user.is_authenticated:
        return 'Forbidden', 403
    results = Category.query.all()
    return render_template('category/category-edit.html', 
                            results = results,
                            segment='category-edit')


@blueprint.route('/delete-category',  methods=["POST", "GET"])
def delete_category():
    if not current_user.is_authenticated:
        return 'Forbidden', 403
    category_id = request.form.get('id')
    query = Category.query.filter_by(id = category_id).first()
    db.session.delete(query)
    db.session.commit()
    return '', 200  

@blueprint.route('/update-category', methods=["POST", "GET"])
def update_category():
    if not current_user.is_authenticated:
        return 'Forbidden', 403
    category_id = request.form.get('id')
    result = Category.query.filter_by(id = category_id).first()
    return jsonify({
                    "id": f"{result.id}",
                    'name': f"{result.name}"
                  })


@blueprint.route('/update-category-action', methods=["POST", "GET"])
def update_category_action():
    if not current_user.is_authenticated:
        return 'Forbidden', 403    
    category_id = request.form.get('id')
    name = request.form.get('name')
    if category_id == '':
        # 新增資料
        q = Category(name = name)
        db.session.add(q)             
        db.session.commit()
        
    else:
        # 更新資料    
        q = Category.query.filter_by(id = category_id).first()
        q.name = name
        db.session.commit()
    
    return redirect('/category-edit')

## Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500
