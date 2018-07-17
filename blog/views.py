from django.shortcuts import render, HttpResponse, redirect, reverse
from django.contrib import auth
from .models import UserInfo, Article, Category, Tag, ArticleUpDown, Comment, Article2Tag, Upload
from django.db.models import Avg, Max, Min, Count
from django.http import JsonResponse
from django.db import transaction
from django.db.models import F
from bs4 import BeautifulSoup
from Blogs import settings
from blog.vcode.vcode import check_code
from io import BytesIO
import json
import os


def wrap(func):
    def inner(*args, **kwargs):
        log_auth = args[0].user.is_authenticated
        if not log_auth:
            return redirect(reverse('login'))
        ret = func(*args, **kwargs)
        return ret

    return inner


def index(request, **kwargs):
    if not kwargs:
        article_list = Article.objects.all()

    else:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'category':
            article_list = Article.objects.filter(category__title=param)
        elif condition == 'tag':
            article_list = Article.objects.filter(tags__title=param)
        else:
            year, month = param.split('/')
            article_list = Article.objects.filter(create_time__year=year,
                                                  create_time__month=month)

    return render(request, 'index.html', locals())


def login(request):

    if request.method == "POST":
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        code = request.POST.get('code')
        if code.upper() != request.session['random_code'].upper():
            return render(request, 'login.html', {'msg': '验证码错误'})
        user_obj = auth.authenticate(username=user, password=pwd)
        if user_obj:
            auth.login(request, user_obj)
            return redirect(reverse('index'))
        return render(request, 'login.html', {'msg': '用户名或者密码错误'})
    return render(request, 'login.html')


def code(request):  # 生成随机验证码

    img, random_code = check_code()
    request.session['random_code'] = random_code
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))


def register(request):
    return render(request, 'register.html')


def homesite(request, username, **kwargs):
    user = UserInfo.objects.filter(username=username).first()

    if not user:
        return render(request, 'not_found.html')

    if not kwargs:
        article_list = Article.objects.filter(user=user)

    else:
        condition = kwargs.get('condition')
        param = kwargs.get('param')

        if condition == 'category':
            article_list = Article.objects.filter(user=user).filter(category__title=param)
        elif condition == 'tag':
            article_list = Article.objects.filter(user=user).filter(tags__title=param)
        else:
            year, month = param.split('/')
            article_list = Article.objects.filter(user=user).filter(create_time__year=year,
                                                                    create_time__month=month)

    return render(request, 'homesite.html', locals())


def article_content(request, article_id):
    article_obj = Article.objects.filter(nid=article_id).first()
    comment_list = Comment.objects.filter(article_id=article_id)
    return render(request, 'article_content.html', locals())


def article_content_site(request, username, article_id):
    article_obj = Article.objects.filter(nid=article_id).first()
    comment_list = Comment.objects.filter(article_id=article_id)
    return render(request, 'article_content_site.html', locals())


def suggest(request):
    article_id = request.POST.get('article_id')
    is_up = json.loads(request.POST.get('is_up'))
    user_id = request.user.pk
    response = {"state": True}

    obj = ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
    if obj:
        response["state"] = False
        response["handle"] = obj.is_up
    else:
        with transaction.atomic():
            ArticleUpDown.objects.create(user_id=user_id, is_up=is_up, article_id=article_id)
            if is_up:
                Article.objects.filter(pk=article_id).update(up_count=F('up_count') + 1)
            else:
                Article.objects.filter(pk=article_id).update(down_count=F('down_count') + 1)

    return JsonResponse(response)


def comment(request):
    user_id = request.user.pk
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    p_comment = request.POST.get("p_comment")
    response = {"state": True}

    with transaction.atomic():
        comment = Comment.objects.create(user_id=user_id, article_id=article_id, content=content,
                                         parent_comment_id=p_comment)
        Article.objects.filter(pk=article_id).update(comment_count=F('comment_count') + 1)

    response["timer"] = comment.create_time.strftime("%Y-%m-%d %X")
    response["content"] = comment.content

    return JsonResponse(response)


def query_article(request):
    article_obj = Article.objects.filter(user=request.user)

    return render(request, 'backstage/query_article.html', locals())


def add_article(request):
    user = request.user
    if request.method == "POST":
        content = request.POST.get('content')
        title = request.POST.get('title')
        cate_id = request.POST.get('cate')
        tag_id = request.POST.getlist('tag')

        soup = BeautifulSoup(content, "html.parser")  # 文章过滤
        for tag in soup.find_all():
            if tag.name in ['script', ]:
                tag.decompose()

        desc = soup.text[0:100]  # <class 'bs4.BeautifulSoup'>

        article_obj = Article.objects.create(title=title, content=str(soup), user=user, category_id=cate_id, desc=desc)

        for tag_pk in tag_id:
            Article2Tag.objects.create(article_id=article_obj.pk, tag_id=tag_pk)

        return redirect(reverse('query_article'))

    blog = user.blog
    category = Category.objects.filter(blog=blog)
    tags = Tag.objects.filter(blog=blog)
    article_obj = Article.objects.filter(user=user)

    return render(request, 'backstage/add_article.html', locals())


def change_article(request, change_id):
    user = request.user
    if request.method == "POST":
        content = request.POST.get('content')
        title = request.POST.get('title')
        cate_id = request.POST.get('cate')
        tag_id = request.POST.getlist('tag')

        soup = BeautifulSoup(content, "html.parser")  # 文章过滤
        for tag in soup.find_all():
            if tag.name in ['script', ]:
                tag.decompose()

        desc = soup.text[0:100]  # <class 'bs4.BeautifulSoup'>

        article_obj = Article.objects.filter(nid=change_id).update(title=title, content=str(soup), user=user,
                                                                   category_id=cate_id, desc=desc)

        for tag_pk in tag_id:
            Article2Tag.objects.filter(article_id=change_id, tag_id=tag_pk).update(article_id=article_obj,
                                                                                   tag_id=tag_pk)

        return redirect(reverse('query_article'))

    blog = request.user.blog
    category = Category.objects.filter(blog=blog)
    tags = Tag.objects.filter(blog=blog)

    article_obj = Article.objects.filter(nid=change_id).first()
    cate_site = article_obj.category
    tag_site = article_obj.tags.all()

    return render(request, 'backstage/change_article.html', locals())


def del_article(request, dele):
    Article.objects.filter(nid=dele).delete()
    Article2Tag.objects.filter(article_id=dele).delete()

    return HttpResponse('删除成功')

@wrap
def upload(request):

    if request.method == "POST":
        file_obj = request.FILES.get('upload_file')
        if not file_obj:
            ret = '请选择要上传的文件'
            file_all = Upload.objects.all()
            return render(request, 'backstage/upload.html', locals())
        else:
            file_name = Upload.objects.create(file_name=file_obj.name)

            with open('static/upload' + file_obj.name, 'wb') as f:
                for line in file_obj:
                    f.write(line)
            return redirect(reverse('upload'))
    file_all = Upload.objects.all()
    return render(request, 'backstage/upload.html', locals())


def upload_img(request):

    obj=request.FILES.get("upload_img")
    name=obj.name

    path=os.path.join(settings.BASE_DIR,"static","upload",name)
    with open(path,"wb") as f:
        for line in obj:
            f.write(line)

    res={
        "error":0,
        "url":"/static/upload/"+name
    }

    # return HttpResponse(json.dumps(res))
    return JsonResponse(res)



