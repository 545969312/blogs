from django import template
from blog.models import Category,Tag,Article,UserInfo
from django.db.models import Count,Avg,Max

register = template.Library()


@register.simple_tag
def mul_tag(x, y):

    return x*y


@register.inclusion_tag("left_region.html")  # 对自定义标签进行装饰，函数里面写标签里面需要的参数
def get_query_data(username):
    user = UserInfo.objects.filter(username=username).first()
    # 查询当前站点对象

    # 查询当前站点每一个分类的名称以及对应的文章数

    cate_list = Category.objects.annotate(c=Count("article__title"))\
        .values_list("title", "c")

    # 查询当前站点每一个标签的名称以及对应的文章数

    tag_list = Tag.objects.annotate(c=Count("article__title"))\
        .values_list("title", "c")

    # 日期归档

    date_list = Article.objects.all().extra(select={"y_m_date": "strftime('%%Y/%%m',create_time)"})\
        .values("y_m_date").annotate(count=Count("title")).values_list("y_m_date","count")

    return {
            "username": username,
            "cate_list": cate_list,
            "tag_list": tag_list,
            "date_list": date_list,
            }


@register.inclusion_tag("left_region_site.html")
def get_query_site(username):
    user = UserInfo.objects.filter(username=username).first()
    # 查询当前站点对象

    blog = user.blog

    print(username)
    # 查询当前站点每一个分类的名称以及对应的文章数

    cate_list = Category.objects.filter(blog=blog).annotate(c=Count("article__title"))\
        .values_list("title", "c")

    # 查询当前站点每一个标签的名称以及对应的文章数

    tag_list = Tag.objects.filter(blog__site_name=username).values('pk').annotate(c=Count("article__title"))\
        .values_list("title", "c")
    print(tag_list)


    # 日期归档

    date_list = Article.objects.filter(user=user).extra(select={"y_m_date": "strftime('%%Y/%%m',create_time)"})\
        .values("y_m_date").annotate(count=Count("title")).values_list("y_m_date","count")

    return {
            "username": username,
            "cate_list": cate_list,
            "tag_list": tag_list,
            "date_list": date_list,
            }